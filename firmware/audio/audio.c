// Module audio du firmware maison : musique IMA ADPCM 4 bits sur le DAC de GPIO26.
// write() decode dans un tampon circulaire, une interruption de timer en sort un
// echantillon a chaque periode. Tampon vide : le DAC garde sa valeur (pas de claquement).
#include "py/runtime.h"
#include "py/mperrno.h"
#include "esp_attr.h"
#include "esp_heap_caps.h"
#include "driver/gptimer.h"
#include "driver/dac_oneshot.h"
#include "hal/dac_ll.h"

#define RING 16384 // puissance de 2 : ~1,5 s a 11025 Hz

static uint8_t *ring;
static volatile uint32_t rd, wr, starved;
static gptimer_handle_t timer;
static dac_oneshot_handle_t dac;
static int pred, idx, vol = 256;

static const int16_t steps[89] = {
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
    50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130, 143, 157, 173, 190, 209, 230,
    253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963,
    1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327,
    3660, 4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487,
    12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767,
};
static const int8_t adjust[8] = {-1, -1, -1, -1, 2, 4, 6, 8};

static bool IRAM_ATTR on_alarm(gptimer_handle_t t, const gptimer_alarm_event_data_t *e, void *ctx) {
    uint32_t r = rd;
    if (r != wr) {
        dac_ll_update_output_value(DAC_CHAN_1, ring[r & (RING - 1)]);
        rd = r + 1;
    } else {
        starved++;
    }
    return false;
}

static uint8_t decode(int n) {
    int step = steps[idx];
    int diff = step >> 3;
    if (n & 1) {
        diff += step >> 2;
    }
    if (n & 2) {
        diff += step >> 1;
    }
    if (n & 4) {
        diff += step;
    }
    pred += (n & 8) ? -diff : diff;
    pred = pred > 32767 ? 32767 : pred < -32768 ? -32768 : pred;
    idx += adjust[n & 7];
    idx = idx < 0 ? 0 : idx > 88 ? 88 : idx;
    return ((pred * vol) >> 16) + 128;
}

static void release(void) {
    if (timer) {
        gptimer_stop(timer);
        gptimer_disable(timer);
        gptimer_del_timer(timer);
        timer = NULL;
    }
    if (dac) {
        dac_oneshot_del_channel(dac);
        dac = NULL;
    }
    if (ring) {
        heap_caps_free(ring);
        ring = NULL;
    }
}

static void check(esp_err_t err) {
    if (err != ESP_OK) {
        release();
        mp_raise_msg_varg(&mp_type_OSError, MP_ERROR_TEXT("audio 0x%x"), err);
    }
}

// start(frequence) : reserve le tampon, le DAC et un timer.
static mp_obj_t audio_start(mp_obj_t rate_in) {
    release();
    int rate = mp_obj_get_int(rate_in);
    ring = heap_caps_malloc(RING, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    if (!ring) {
        mp_raise_OSError(MP_ENOMEM);
    }
    rd = wr = starved = 0;
    pred = idx = 0;
    dac_oneshot_config_t dc = {.chan_id = DAC_CHAN_1};
    check(dac_oneshot_new_channel(&dc, &dac));
    check(dac_oneshot_output_voltage(dac, 128));
    gptimer_config_t tc = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = 10000000,
    };
    check(gptimer_new_timer(&tc, &timer));
    gptimer_event_callbacks_t cb = {.on_alarm = on_alarm};
    check(gptimer_register_event_callbacks(timer, &cb, NULL));
    gptimer_alarm_config_t ac = {
        .alarm_count = (10000000 + rate / 2) / rate,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = true,
    };
    check(gptimer_set_alarm_action(timer, &ac));
    check(gptimer_enable(timer));
    check(gptimer_start(timer));
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(audio_start_obj, audio_start);

// write(buf, debut, fin) : decode buf[debut:fin] tant qu'il y a de la place, rend le nombre d'octets pris.
static mp_obj_t audio_write(mp_obj_t buf_in, mp_obj_t start_in, mp_obj_t end_in) {
    mp_buffer_info_t bi;
    mp_get_buffer_raise(buf_in, &bi, MP_BUFFER_READ);
    size_t a = mp_obj_get_int(start_in), b = mp_obj_get_int(end_in);
    if (!ring || b > bi.len || a >= b) {
        return MP_OBJ_NEW_SMALL_INT(0);
    }
    size_t n = b - a, room = (RING - (wr - rd)) / 2;
    if (n > room) {
        n = room;
    }
    const uint8_t *p = (const uint8_t *)bi.buf + a;
    uint32_t w = wr;
    for (size_t i = 0; i < n; i++) {
        ring[w++ & (RING - 1)] = decode(p[i] & 15);
        ring[w++ & (RING - 1)] = decode(p[i] >> 4);
    }
    wr = w;
    return MP_OBJ_NEW_SMALL_INT(n);
}
static MP_DEFINE_CONST_FUN_OBJ_3(audio_write_obj, audio_write);

// reset() : debut d'un nouveau flux (etat du decodeur a zero), le tampon continue.
static mp_obj_t audio_reset(void) {
    pred = idx = 0;
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_reset_obj, audio_reset);

// volume(0..256)
static mp_obj_t audio_volume(mp_obj_t v_in) {
    int v = mp_obj_get_int(v_in);
    vol = v < 0 ? 0 : v > 256 ? 256 : v;
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(audio_volume_obj, audio_volume);

// stats() : (echantillons en attente, periodes sans echantillon depuis start)
static mp_obj_t audio_stats(void) {
    mp_obj_t t[2] = {mp_obj_new_int(ring ? wr - rd : 0), mp_obj_new_int(starved)};
    return mp_obj_new_tuple(2, t);
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_stats_obj, audio_stats);

static mp_obj_t audio_stop(void) {
    release();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_stop_obj, audio_stop);

static const mp_rom_map_elem_t audio_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_audio) },
    { MP_ROM_QSTR(MP_QSTR_start), MP_ROM_PTR(&audio_start_obj) },
    { MP_ROM_QSTR(MP_QSTR_write), MP_ROM_PTR(&audio_write_obj) },
    { MP_ROM_QSTR(MP_QSTR_reset), MP_ROM_PTR(&audio_reset_obj) },
    { MP_ROM_QSTR(MP_QSTR_volume), MP_ROM_PTR(&audio_volume_obj) },
    { MP_ROM_QSTR(MP_QSTR_stats), MP_ROM_PTR(&audio_stats_obj) },
    { MP_ROM_QSTR(MP_QSTR_stop), MP_ROM_PTR(&audio_stop_obj) },
};
static MP_DEFINE_CONST_DICT(audio_globals, audio_globals_table);

const mp_obj_module_t audio_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&audio_globals,
};

MP_REGISTER_MODULE(MP_QSTR_audio, audio_module);
