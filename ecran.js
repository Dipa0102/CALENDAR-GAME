/* Ecran 240x320 : memes vues et memes jeux que le programme de la carte. */
(function () {
  const W = 240, H = 320, HUD = 20, TAB = 28;
  const NIGHT = "#122028", MAGENTA = "#DB352B", INK = "#F6EBDC", LILAC = "#AFA08E";
  const SKY = "#6094B6", SUN = "#E25241", GOLD = "#F6EBDC", LINE = "#1E3A48", LIME = "#3CFF7A";
  const ASPHALT = "#12121C", PANEL = "#1C1C2C", WHITE = "#FFFFFF", BLACK = "#000000";
  const MUTED = "#9696AA", YELLOW = "#FFD200", RED = "#DC2832", GREEN = "#28D25A";
  const CYAN = "#00D2FF", ORANGE = "#FF8C00", PINK = "#FF78B4", SLATE = "#122028";
  const CREAM = "#F6EBDC", REDP = "#DB352B", TEAL = "#0E526C", GREY = "#78788C";
  const DOOR = "#0E2A36", VIOLET = "#321050";
  const BANDS = ["#DB352B", "#F6EBDC", "#0E526C", "#B42A22", "#6094B6"];
  const MOIS = ["JANV","FEVR","MARS","AVRIL","MAI","JUIN","JUIL","AOUT","SEPT","OCT","NOV","DEC"];
  const MOIS_LONG = ["JANVIER","FEVRIER","MARS","AVRIL","MAI","JUIN","JUILLET","AOUT","SEPTEMBRE","OCTOBRE","NOVEMBRE","DECEMBRE"];
  const JOURS = ["L","M","M","J","V","S","D"];
  const JOURS_LONG = ["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI","SAMEDI","DIMANCHE"];
  const JOURS3 = ["LUN","MAR","MER","JEU","VEN","SAM","DIM"];
  const AZ = ["AZERTYUIOP","QSDFGHJKLM","WXCVBN'-./"];
  const NUM = ["1234567890","@#&_+*=!?%","$()[]:;,<>"];
  const THEMES = [["anniv","ANNIV"],["event","EVENT"],["oubli","OUBLI"],["rappel","RAPPEL"],["tache","TACHE"]];
  const WX_TXT = {sun:"CIEL CLAIR", partly:"PEU NUAGEUX", cloud:"NUAGEUX", rain:"PLUIE", storm:"ORAGE"};
  const HELP = {
    1:["GLISSE LA RAQUETTE","LA BALLE CASSE","LES BRIQUES"],
    2:["GLISSE LE DOIGT","LE VAISSEAU TIRE","TOUT SEUL"],
    3:["POSE LE DOIGT","LE SERPENT VA","VERS TON DOIGT"],
    4:["GLISSE LE DOIGT POUR","RENVOYER LA BALLE","PREMIER A 7 POINTS"],
    5:["GLISSE : LE CANON","DOIGT POSE : TIR","UN SEUL MISSILE"],
    6:["VISE AVEC LE DOIGT","DOIGT POSE : CA TIRE","LES ROCHERS SE FENDENT"],
    7:["TOUCHE AU-DESSUS : AVANCE","EN DESSOUS : RECULE","EVITE LES VOITURES"],
    8:["GLISSE LE DOIGT","EVITE LES BOMBES","RAMASSE LES PIECES"],
    9:["GLISSE LE DOIGT POUR","CHANGER DE FILE","NE TOUCHE PERSONNE"],
    10:["DOIGT POSE : MONTE","DOIGT LEVE : DESCEND","EVITE LES PAROIS"],
    11:["TOUCHE DEUX CARTES","TROUVE LES PAIRES","AVANT LA FIN DU TEMPS"],
    12:["COMPLETE DES LIGNES","BOUTONS TOURNE ET BAS","BAS DEUX FOIS : CHUTE"],
    13:["TOUCHE L OISEAU","3 TIRS PAR OISEAU","NE LE LAISSE PAS FUIR"],
    14:["SUIS LE DOIGT","TIRE SUR LES LANDERS","SAUVE LES HUMAINS"],
    15:["GARDE LE DOIGT","LE MINEUR CREUSE","DIAMANTS PUIS SORTIE"],
    16:["DOIGT POSE : MOTEUR","LE DOIGT GUIDE","POSE-TOI EN DOUCEUR"],
    17:["LE DOIGT DIRIGE","REBONDIS SUR LES BARRES","NE TOMBE PAS"],
    18:["DOIGT : TREMPLIN","3 REBONDS PUIS L AMBU","NE LES LAISSE PAS TOMBER"],
    19:["TIRE SUR LES ZOMBIES","VISE LA TETE : BONUS","CAISSE : RECHARGE"],
    20:["LA BILLE SUIT TON DOIGT","RAMASSE LES ETOILES","SORTIE AVANT LA FIN"],
    21:["GLISSE LE CHAUDRON","ATTRAPE LES CRISTAUX","EVITE LES BOMBES"],
    22:["TOUCHE LA CASE QUI","S ALLUME AU PLUS VITE","BLANCHE : NE TOUCHE PAS"],
    23:["TOUCHE UN AIGUILLAGE","POUR LE BASCULER","CHAQUE TRAIN A SA GARE"],
    24:["GLISSE : LE VAISSEAU","IL TIRE TOUT SEUL","4 BOSS, 3 VIES"],
    25:["4 EPREUVES, 3 VIES","ALTERNE GAUCHE DROITE","SAUT AVANT LA LIGNE"]
  };
  const TITLES = ["","MAGIC HARRY","STAR RAID","SERPENT 80","PING 80","ENVAHISSEURS","ROCHERS 80","ROUTE 80","BOMB DODGE","TURBO 80","HELICO 80","PAIRES 80","BLOCS 80","CIBLES 80","DEFENSEUR","MINEUR 80","ALUNISSAGE","SAUTEUR 80","FIRE ESCAPE","ZOMBIE NIGHT","LABYRINTHE","CRYSTAL CATCH","REACTION 80","AIGUILLAGES","BOSS RUSH","CHAMPIONNAT"];

  const FONT = Uint8Array.from(atob("AAAAAAAAAAAYGBgYGAAYAGxsJAAAAAAAbGz+bP5sbAAYPlg8GnwYAADGzBgwZsYAOGw4dtzMdgAYGDAAAAAAAAwYMDAwGAwAMBgMDAwYMAAAZjz/PGYAAAAYGH4YGAAAAAAAAAAYGDAAAAB+AAAAAAAAAAAAGBgABgwYMGDAgAA8Zm52ZmY8ABg4GBgYGH4APGYGDBgwfgA8ZgYcBmY8AAwcPGx+DAwAfmB8BgZmPAAcMGB8ZmY8AH4GDBgwMDAAPGZmPGZmPAA8ZmY+Bgw4AAAYGAAAGBgAABgYAAAYGDAMGDBgMBgMAAAAfgB+AAAAMBgMBgwYMAA8ZgYMGAAYADxmbmpuYDwAGDxmZn5mZgB8ZmZ8ZmZ8ADxmYGBgZjwAeGxmZmZseAB+YGB8YGB+AH5gYHxgYGAAPGZgbmZmPABmZmZ+ZmZmAH4YGBgYGH4APgwMDAxsOABmbHhweGxmAGBgYGBgYH4Axu7+1sbGxgBmdn5+bmZmADxmZmZmZjwAfGZmfGBgYAA8ZmZmdmw2AHxmZnx4bGYAPGZgPAZmPAB+GBgYGBgYAGZmZmZmZjwAZmZmZmY8GADGxsbW/u7GAGZmPBg8ZmYAZmZmPBgYGAB+BgwYMGB+ADwwMDAwMDwAwGAwGAwGAgA8DAwMDAw8ABg8ZgAAAAAAAAAAAAAAAP8YGAwAAAAAAAAAPAY+Zj4AYGB8ZmZmfAAAADxmYGY8AAYGPmZmZj4AAAA8Zn5gPAAcMDB8MDAwAAAAPmZmPgY8YGB8ZmZmZgAYADgYGBg8AAwAHAwMDGw4YGBmbHhsZgA4GBgYGBg8AAAA7P7WxsYAAAB8ZmZmZgAAADxmZmY8AAAAfGZmfGBgAAA+ZmY+BgYAAGx2YGBgAAAAPmA8BnwAMDB8MDAwHAAAAGZmZmY+AAAAZmZmPBgAAADG1v58bAAAAGY8GDxmAAAAZmZmPgY8AAB+DBgwfgAOGBhwGBgOABgYGBgYGBgAcBgYDhgYcAB23AAAAAAAAAAAAAAAAAAA"), c => c.charCodeAt(0));

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const pad = (n, l = 2) => String(n).padStart(l, "0");
  const fold = s => (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase();
  const keyOf = (y, m, d) => pad(y, 4) + "-" + pad(m) + "-" + pad(d);
  const leap = y => y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
  const dim = (y, m) => m === 2 ? (leap(y) ? 29 : 28) : [0,31,28,31,30,31,30,31,31,30,31,30,31][m];
  function dowMon(y, m, d) {
    const t = [0,3,2,5,0,3,5,1,4,6,2,4];
    const yy = y - (m < 3 ? 1 : 0);
    const sun = (yy + (yy / 4 | 0) - (yy / 100 | 0) + (yy / 400 | 0) + t[m - 1] + d) % 7;
    return (sun + 6) % 7;
  }
  const hit = (px, py, x, y, w, h, m = 0) => px >= x - m && px < x + w + m && py >= y - m && py < y + h + m;
  const store = {
    load(k, d) { try { const v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } },
    save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };

  let cv, g, opt, mode = "cal", game = null;
  const P = {x: 120, y: 160, down: false, tap: false, hold: 0};
  const keys = {};
  const st = {
    vy: 0, vm: 0, sel: null, fake: null, tz: 1, vol: 6, city: 0,
    test: false, muet: false, seen: "", notes: null, rec: null,
    msg: "", theme: "anniv", buf: "", num: false, low: true, edit: "",
    gift: 0, blink: 0, idle: 0, saverFrom: "cal", saverImg: 0, saverNext: 0,
    sheet: null, wifi: false, ptr: 0, clock: false, field: "h",
    bufH: "", bufD: "", bat: 87, usb: false
  };

  function nowDate() {
    if (!st.fake) return new Date();
    const f = st.fake;
    return new Date(f.y, f.m - 1, f.d, f.hh, f.mm, f.ss || 0);
  }
  function parts() {
    const n = nowDate();
    return {y: n.getFullYear(), m: n.getMonth() + 1, d: n.getDate(), hh: n.getHours(), mm: n.getMinutes(), ss: n.getSeconds(), wd: n.getDay()};
  }
  function todayTuple() { const p = parts(); return [p.y, p.m, p.d]; }
  function unlocked(day) {
    if (day === 1 || st.test) return true;
    const p = parts();
    return p.m === 12 && p.d >= day && day <= 25;
  }
  function countdown() {
    const p = parts();
    if (p.m === 12) return p.d <= 25 ? "PORTE " + p.d + " OUVERTE !" : "";
    const a = new Date(p.y, 11, 1), b = new Date(p.y, p.m - 1, p.d);
    return "J-" + Math.round((a - b) / 86400000) + " AVANT LA PORTE 1";
  }

  function text(s, x, y, col, scale) {
    scale = scale || 1;
    g.fillStyle = col;
    for (let i = 0; i < s.length; i++) {
      let o = s.charCodeAt(i);
      if (o < 32 || o > 127) o = 63;
      const base = (o - 32) * 8;
      for (let row = 0; row < 8; row++) {
        const bits = FONT[base + row];
        let c = 0;
        while (c < 8) {
          if (bits & (0x80 >> c)) {
            const a = c;
            while (c < 8 && (bits & (0x80 >> c))) c++;
            g.fillRect(x + (i * 8 + a) * scale, y + row * scale, (c - a) * scale, scale);
          } else c++;
        }
      }
    }
  }
  const tw = (s, scale) => s.length * 8 * (scale || 1);
  function textC(s, y, col, scale, shadow) {
    const x = (W - tw(s, scale)) / 2 | 0;
    if (shadow) text(s, x + (scale || 1), y + (scale || 1), shadow, scale);
    text(s, x, y, col, scale);
  }
  function button(x, y, w, h, label, bg, fg) {
    g.fillStyle = bg; g.fillRect(x, y, w, h);
    g.strokeStyle = CREAM; g.strokeRect(x + .5, y + .5, w - 1, h - 1);
    text(label, x + (w - tw(label)) / 2 | 0, y + (h - 8) / 2 | 0, fg);
  }
  function bands(y) { BANDS.forEach((c, i) => { g.fillStyle = c; g.fillRect(0, y + i * 3, W, 3); }); }
  function menuBtn() {
    g.fillStyle = REDP; g.fillRect(2, 1, 46, 18);
    g.strokeStyle = CREAM; g.strokeRect(2.5, 1.5, 45, 17);
    text("MENU", 9, 6, CREAM);
  }
  function tabs(active) {
    const y = H - TAB, labs = [["CAL","cal"],["METEO","meteo"],["JEU","jeu"],["REGL","set"]];
    g.fillStyle = BLACK; g.fillRect(0, y, W, TAB);
    labs.forEach((lab, i) => {
      const x = i * 60, bg = lab[1] === active ? MAGENTA : DOOR;
      g.fillStyle = bg; g.fillRect(x + 1, y + 2, 58, TAB - 4);
      text(lab[0], x + 8, y + 10, INK);
    });
  }
  function tabAt(x, y) {
    if (y < H - TAB) return null;
    return ["cal","meteo","jeu","set"][Math.min(3, x / 60 | 0)];
  }
  function battery(top, bg) {
    const x = W - 6 - 17, y = top + 2, pct = st.bat;
    g.fillStyle = bg; g.fillRect(150, top, 90, 14);
    g.strokeStyle = WHITE; g.strokeRect(x + .5, y + .5, 14, 8);
    g.fillStyle = WHITE; g.fillRect(x + 15, y + 2, 2, 5);
    g.fillStyle = NIGHT; g.fillRect(x + 1, y + 1, 13, 7);
    const w = (11 * pct + 50) / 100 | 0;
    g.fillStyle = st.usb || pct >= 50 ? LIME : pct >= 20 ? GOLD : "#FF4436";
    if (w) g.fillRect(x + 2, y + 2, w, 5);
    const s = pct + "%";
    text(s, x - 8 - tw(s), top + 3, st.usb || pct >= 20 ? (st.usb ? LIME : WHITE) : "#FF4436");
  }
  function wxIcon(kind, cx, cy, s) {
    const pix = (fn, col, ox, oy) => {
      ox = ox || 0; oy = oy || 0;
      g.fillStyle = col;
      for (let j = -7; j <= 7; j++) for (let i = -8; i <= 8; i++) if (fn(i - ox, j - oy)) g.fillRect(cx + i * s - s / 2 | 0, cy + j * s - s / 2 | 0, s, s);
    };
    const disc = r => (x, y) => x * x + y * y <= r * r;
    const cloud = (x, y) => ((x + 3) ** 2 + (y - 1) ** 2 <= 10) || ((x - 1) ** 2 + (y + 1) ** 2 <= 14) || ((x - 4) ** 2 + (y - 1.5) ** 2 <= 8) || (y >= 1 && y <= 4 && x >= -6 && x <= 7);
    if (kind === "sun") { pix(disc(3.2), "#FFD23F"); pix((x, y) => { const r = Math.hypot(x, y); return r >= 4.6 && r <= 6.2 && Math.abs(Math.sin(Math.atan2(y, x) * 4)) < .45; }, "#FF8A1F"); }
    else if (kind === "partly") { pix(disc(3), "#FFD23F", -3, -3); pix(cloud, "#F4D6EA", 1, 1); }
    else if (kind === "cloud") pix(cloud, "#C8C4D8", 0, -1);
    else if (kind === "rain") { pix(cloud, "#9A93B3", 0, -2); pix((x, y) => y >= 4 && y <= 6 && x > -6 && x < 7 && ((x + y) % 3 + 3) % 3 === 0, "#3BE3FF"); }
    else { pix(cloud, "#6E6788", 0, -2); pix((x, y) => [[1,3],[0,4],[-1,5],[0,5],[1,5],[0,6]].some(p => p[0] === x && p[1] === y), "#FFD23F"); }
  }
  function forecast() {
    const c = (opt.cities || [])[st.city] || ["PARIS","Paris",19,10];
    const base = parts();
    const out = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(base.y, base.m - 1, base.d + i);
      const cond = ["sun","partly","cloud","rain","partly","sun","storm"][(i + st.city * 2) % 7];
      const min = c[3] + Math.round(2 * Math.sin(i * 1.1 + st.city));
      const max = Math.max(min + 3, c[2] + Math.round(3 * Math.sin(i * 1.3 + st.city)) - (cond === "rain" || cond === "storm" ? 2 : 0));
      out.push({y: d.getFullYear(), m: d.getMonth() + 1, d: d.getDate(), wd: d.getDay(), cond, min, max, key: keyOf(d.getFullYear(), d.getMonth() + 1, d.getDate())});
    }
    return out;
  }
  function cityName() {
    const c = (opt.cities || [])[st.city];
    return fold(c ? c[1] : "PARIS");
  }
  function tempNow() {
    const f = forecast()[0];
    return Math.round((f.min + f.max) / 2);
  }

  function defaultNotes() {
    const p = parts();
    const add = n => { const d = new Date(p.y, p.m - 1, p.d + n); return keyOf(d.getFullYear(), d.getMonth() + 1, d.getDate()); };
    const o = {};
    o[add(2)] = {t: "anniv", txt: "ANNIV. LEA"};
    o[add(5)] = {t: "event", txt: "DENTISTE 14H30"};
    o[add(9)] = {t: "event", txt: "CONCERT ROCK"};
    return o;
  }
  function noteIcon(kind, x, y) {
    if (kind === "anniv") { g.fillStyle = RED; g.fillRect(x + 1, y, 8, 5); g.fillStyle = PINK; g.fillRect(x + 3, y + 5, 4, 4); g.fillStyle = WHITE; g.fillRect(x + 2, y + 1, 2, 2); }
    else if (kind === "event") { g.fillStyle = WHITE; g.fillRect(x + 1, y, 2, 9); g.fillStyle = GREEN; g.fillRect(x + 3, y, 6, 5); }
    else if (kind === "oubli") { g.fillStyle = YELLOW; g.fillRect(x + 3, y, 4, 4); g.fillRect(x + 1, y + 3, 8, 6); g.fillStyle = BLACK; g.fillRect(x + 4, y + 2, 2, 2); }
    else if (kind === "rappel") { g.fillStyle = YELLOW; g.fillRect(x + 3, y, 4, 2); g.fillStyle = CYAN; g.fillRect(x + 2, y + 2, 6, 5); g.fillStyle = WHITE; g.fillRect(x + 4, y + 7, 2, 2); }
    else { g.fillStyle = ORANGE; g.fillRect(x, y, 10, 10); g.fillStyle = WHITE; g.fillRect(x + 2, y + 4, 6, 2); }
  }
  function miniGift(x, y, s, bg) {
    const rows = [".yy...yy.","y..y.y..y",".yyyyyyy.","RRRRyRRRR","rrrryrrrr",".rrryrrr.",".rrryrrr.",".rrryrrr.",".RRRyRRR."];
    const pal = {y: "#FFD728", Y: "#C88C14", r: "#E6283C", R: "#961432", k: "#1E0A28"};
    rows.forEach((row, j) => { for (let i = 0; i < row.length; i++) if (row[i] !== ".") { g.fillStyle = pal[row[i]]; g.fillRect(x + i * s, y + j * s, s, s); } });
  }
  function bigGift(x, y) {
    const rows = ["..kkk......kkk..",".kyyyk....kyyyk.",".kyYyyk..kyyYyk.","..kyYyykkyyYyk..","...kkyyyyyykk...","kkkkkkkyykkkkkkk","kwrrrrryYrrrrrRk","kRRRRRRyYRRRRRRk","kkkkkkkyykkkkkkk",".kwrrrryYrrrrRk.",".krrrrryYrrrrRk.",".krrrrryYrrrrRk.",".krrrrryYrrrrRk.",".kRRRRRyYRRRRRk.",".kkkkkkkkkkkkkk."];
    const pal = {k:"#1E0A28", r:"#E6283C", R:"#961432", w:"#FF96A0", y:"#FFD728", Y:"#C88C14"};
    rows.forEach((row, j) => { for (let i = 0; i < row.length; i++) if (row[i] !== ".") { g.fillStyle = pal[row[i]]; g.fillRect(x + i * 5, y + j * 5, 5, 5); } });
  }

  function drawCal() {
    const p = parts(), fc = {};
    forecast().forEach(f => { fc[f.key] = f.cond; });
    g.fillStyle = NIGHT; g.fillRect(0, 0, W, H);
    g.fillStyle = MAGENTA; g.fillRect(0, 0, W, 22);
    text("<", 6, 7, WHITE);
    text(MOIS[st.vm - 1] + " " + st.vy, 26, 7, WHITE);
    text(">", 112, 7, WHITE);
    const clk = pad(p.hh) + (p.ss % 2 ? " " : ":") + pad(p.mm);
    text(clk, 130, 7, WHITE);
    battery(4, MAGENTA);
    JOURS.forEach((j, i) => text(j, i * 34 + 13, 26, i >= 5 ? SUN : SKY));
    const first = dowMon(st.vy, st.vm, 1), nd = dim(st.vy, st.vm);
    const today = todayTuple();
    for (let day = 1; day <= nd; day++) {
      const idx = first + day - 1, x = (idx % 7) * 34, yy = 37 + (idx / 7 | 0) * 31;
      const s = String(day), sx = x + 17 - s.length * 4;
      const isToday = today[0] === st.vy && today[1] === st.vm && today[2] === day;
      if (isToday) { g.fillStyle = SKY; g.fillRect(x + 6, yy + 1, 22, 10); text(s, sx, yy + 2, NIGHT); }
      else text(s, sx, yy + 2, idx % 7 >= 5 ? LILAC : INK);
      const k = keyOf(st.vy, st.vm, day);
      const gift = st.vm === 12 && day <= 25 && unlocked(day);
      if (fc[k]) wxIcon(fc[k], x + (gift ? 12 : 16), yy + 20, 1);
      if (gift) miniGift(x + 22, yy + 16, 1);
      if (st.notes[k]) { g.fillStyle = "#F6EBDC"; g.fillRect(x + 29, yy + 2, 3, 3); }
      if (st.sel && st.sel[0] === st.vy && st.sel[1] === st.vm && st.sel[2] === day) {
        g.strokeStyle = GOLD; g.strokeRect(x + 1.5, yy + .5, 31, 29);
      }
    }
    g.fillStyle = LINE; g.fillRect(6, 225, W - 12, 2);
    text("A VENIR", 6, 231, GOLD);
    const wt = cityName().slice(0, 12) + " " + tempNow() + "C";
    text(wt, W - 6 - tw(wt), 231, SKY);
    const start = keyOf(p.y, p.m, p.d);
    const ev = Object.keys(st.notes).filter(k => k >= start).sort().slice(0, 3);
    if (!ev.length) text("RIEN DE PREVU", 6, 242, MUTED);
    ev.forEach((k, i) => {
      const yy = 242 + i * 12, note = st.notes[k];
      text(k.slice(8, 10) + "/" + k.slice(5, 7), 6, yy, SKY);
      noteIcon(note.t || "tache", 50, yy - 1);
      text(fold(note.txt).slice(0, 20), 66, yy, INK);
    });
    const cd = countdown();
    if (cd && p.ss % 2 === 0) textC(cd, 280, LIME);
    tabs("cal");
  }

  function drawMeteo() {
    const f = forecast(), kind = f[0].cond;
    g.fillStyle = ASPHALT; g.fillRect(0, 0, W, H);
    text("METEO", 8, 6, YELLOW, 2);
    text(cityName().slice(0, 16), 8, 28, WHITE);
    text(tempNow() + " C", 8, 48, CYAN, 2);
    text(WX_TXT[kind] || "NUAGEUX", 8, 70, WHITE);
    wxIcon(kind, 200, 52, 3);
    button(8, 92, 100, 24, "VILLE", YELLOW, BLACK);
    button(116, 92, 116, 24, "ACTUALISER", GREEN, BLACK);
    text((st.msg || "MAJ " + pad(parts().hh) + ":" + pad(parts().mm)).slice(0, 26), 8, 122, MUTED);
    let y = 136;
    f.forEach(row => {
      g.fillStyle = PANEL; g.fillRect(4, y, 232, 20);
      const lab = JOURS3[(dowMon(row.y, row.m, row.d))] + " " + pad(row.d);
      text(lab, 8, y + 6, WHITE);
      wxIcon(row.cond, 78, y + 10, 1);
      text("MF", 92, y + 6, MUTED);
      text(String(row.min), 150, y + 6, CYAN);
      text(String(row.max), 196, y + 6, ORANGE);
      y += 21;
    });
    tabs("meteo");
  }

  function drawSet() {
    const p = parts();
    const rows = [["HEURE", pad(p.hh), "hh"],["MIN", pad(p.mm), "mi"],["JOUR", pad(p.d), "dd"],["MOIS", pad(p.m), "mo"],["ANNEE", String(p.y), "yy"],["FUSEAU", (st.tz >= 0 ? "+" : "") + st.tz, "tz"],["VOLUME", st.vol ? String(st.vol) : "MUET", "vol"]];
    g.fillStyle = ASPHALT; g.fillRect(0, 0, W, H);
    let yy = 2;
    rows.forEach(r => {
      text(r[0], 4, yy + 4, MUTED);
      text(r[1], 78, yy + 4, WHITE);
      button(140, yy, 40, 20, "-", PANEL, WHITE);
      button(186, yy, 40, 20, "+", YELLOW, BLACK);
      yy += 22;
    });
    button(8, yy + 2, 108, 22, "SYNC NET", CYAN, BLACK);
    button(124, yy + 2, 108, 22, "WIFI", GREEN, BLACK);
    text((st.msg || "").slice(0, 26), 8, yy + 28, YELLOW);
    text(st.wifi ? "DEMO-WIFI" : "(pas de wifi)", 8, yy + 40, MUTED);
    button(8, 210, 224, 28, "CLAVIER", CYAN, BLACK);
    button(8, 244, 224, 32, "POINTEUR", YELLOW, BLACK);
    tabs("set");
  }

  function drawKbd(y0, numeric) {
    const rows = numeric ? NUM : AZ.map(r => st.low ? r.toLowerCase() : r);
    const keys = [];
    rows.forEach((row, r) => {
      const kw = W / row.length | 0;
      for (let i = 0; i < row.length; i++) {
        const x = i * kw, y = y0 + r * 22;
        g.fillStyle = PANEL; g.fillRect(x + 1, y, kw - 2, 20);
        text(row[i], x + 4, y + 6, WHITE);
        keys.push([row[i], x, y, kw, 22]);
      }
    });
    const y = y0 + 66;
    button(4, y, 70, 22, "EFF", ORANGE, BLACK);
    button(78, y, 84, 22, "ESPACE", PANEL, WHITE);
    keys.push(["BS", 4, y, 70, 22], [" ", 78, y, 84, 22]);
    if (!numeric) {
      button(166, y, 70, 22, st.low ? "abc" : "MAJ", st.low ? CYAN : YELLOW, BLACK);
      keys.push(["SH", 166, y, 70, 22]);
    }
    return keys;
  }
  function drawNote() {
    const s = st.sel || todayTuple();
    g.fillStyle = ASPHALT; g.fillRect(0, 0, W, H);
    text(pad(s[2]) + " " + MOIS[s[1] - 1] + " " + s[0], 4, 2, YELLOW);
    THEMES.forEach((th, i) => {
      const x = i * 48, on = th[0] === st.theme;
      g.fillStyle = on ? YELLOW : PANEL; g.fillRect(x + 1, 14, 46, 36);
      noteIcon(th[0], x + 18, 16);
      text(th[1].slice(0, 4), x + 6, 36, on ? BLACK : WHITE);
    });
    g.fillStyle = BLACK; g.fillRect(4, 54, 232, 16);
    text(st.buf.slice(-26), 6, 58, WHITE);
    st._keys = drawKbd(74, st.num);
    g.fillStyle = LINE; g.fillRect(6, 166, W - 12, 2);
    const row = forecast().find(f => f.key === st.edit) || forecast()[0];
    text(row.key === keyOf(parts().y, parts().m, parts().d) ? "METEO AUJOURD HUI" : "METEO DU JOUR", 8, 172, MUTED);
    wxIcon(row.cond, 28, 196, 2);
    text(row.max + " / " + row.min + " C", 56, 186, WHITE);
    text(WX_TXT[row.cond] || "", 56, 198, SKY);
    button(4, H - 26, 70, 22, "VIDE", RED, WHITE);
    button(80, H - 26, 70, 22, st.num ? "ABC" : "123", PANEL, WHITE);
    button(156, H - 26, 80, 22, "OK", GREEN, BLACK);
  }
  function drawJeu() {
    g.fillStyle = SLATE; g.fillRect(0, 0, W, H);
    bands(0);
    textC("CALENDAR GAME", 18, CREAM, 2, REDP);
    if (st.test) text("TEST", 196, 38, RED);
    text(st.muet ? "MUET" : "SON", 4, 38, st.muet ? GREY : CREAM);
    const played = st.rec.played || [];
    const today = todayTuple();
    for (let day = 1; day <= 25; day++) {
      const r = (day - 1) / 5 | 0, c = (day - 1) % 5;
      const x = 5 + c * 46, y = 46 + r * 48, w = 42, h = 44;
      const open = unlocked(day);
      g.fillStyle = open ? DOOR : SLATE;
      g.fillRect(x, y, w, h);
      g.strokeStyle = open ? (day === today[2] && today[1] === 12 ? CREAM : REDP) : "#1E3A48";
      g.strokeRect(x + .5, y + .5, w - 1, h - 1);
      if (open) miniGift(x + (w - 18) / 2 | 0, y + 4, 2);
      else {
        g.fillStyle = GREY;
        g.fillRect(x + 14, y + 8, 14, 10);
        g.strokeRect(x + 16.5, y + 4.5, 9, 8);
      }
      const s = String(day);
      text(s, x + (w - s.length * 8) / 2 | 0, y + 28, open ? (played.includes(day) ? CREAM : WHITE) : GREY);
    }
    button(2, 294, W - 4, 24, "RETOUR AU CALENDRIER", REDP, CREAM);
  }
  function drawGift() {
    drawCal();
    const x = 16, y = 56, w = 208, h = 212, day = st.gift;
    g.fillStyle = SLATE; g.fillRect(x, y, w, h);
    g.strokeStyle = TEAL; g.strokeRect(x + .5, y + .5, w - 1, h - 1);
    g.strokeStyle = REDP; g.strokeRect(x + 2.5, y + 2.5, w - 5, h - 5);
    BANDS.forEach((c, i) => { g.fillStyle = c; g.fillRect(x + 4, y + 4 + i * 3, w - 8, 3); });
    g.fillStyle = RED; g.fillRect(194, 58, 28, 22);
    g.strokeStyle = WHITE; g.strokeRect(194.5, 58.5, 27, 21);
    text("X", 203, 65, WHITE);
    textC(day + " DECEMBRE", y + 26, CREAM, 2, REDP);
    bigGift((W - 80) / 2 | 0, 108);
    const played = (st.rec.played || []).includes(day);
    textC(played ? TITLES[day] : "SURPRISE !", y + 150, CREAM);
    const best = st.rec[String(day)] || 0;
    if (best) textC("RECORD " + pad(best, 6), y + 164, GREY);
    if ((st.blink | 0) % 2 === 0) textC("TOUCHE LE CADEAU", y + 134, CREAM);
    button(x + w - 90, y + h - 30, 80, 22, "JOUER", "#289646", WHITE);
    button(x + 10, y + h - 30, 80, 22, "NOTE", TEAL, CREAM);
  }
  function drawLocked() {
    g.fillStyle = SLATE; g.fillRect(0, 0, W, H);
    bands(60);
    textC("JOUR " + st.day, 90, CREAM, 2);
    textC(TITLES[st.day], 130, CREAM, TITLES[st.day].length > 12 ? 1 : 2, REDP);
    textC("S OUVRE LE " + st.day + " DEC", 180, CREAM);
    textC("APPUIE LONG SUR LE TITRE", 210, GREY);
    textC("DE LA SALLE : MODE TEST", 222, GREY);
    textC("TOUCHE POUR REVENIR", 280, CREAM);
  }
  function drawSaver() {
    g.fillStyle = NIGHT; g.fillRect(0, 0, W, H);
    const img = st.sheet;
    if (img && img.complete && img.naturalWidth) {
      const COLS = [[24,322],[336,618],[636,922],[937,1228]];
      const ROWS = [[257,489],[558,771],[867,1062]];
      const i = st.saverImg % 12, c = COLS[i % 4], r = ROWS[i / 4 | 0];
      g.drawImage(img, c[0] + 4, r[0] + 40, c[1] - c[0] - 8, r[1] - r[0] - 44, 0, 0, 240, 150);
    } else {
      g.fillStyle = TEAL; g.fillRect(0, 0, W, 150);
      textC("CALENDAR GAME", 70, CREAM, 2, REDP);
    }
    BANDS.forEach((c, i) => { g.fillStyle = c; g.fillRect(0, 152 + i * 3, W, 3); });
    const p = parts();
    const clk = pad(p.hh) + ":" + pad(p.mm);
    text(clk, 23, 183, MAGENTA, 5);
    text(clk, 20, 180, GOLD, 5);
    const ds = JOURS_LONG[(p.wd + 6) % 7] + " " + p.d + " " + MOIS_LONG[p.m - 1];
    textC(ds.length > 28 ? ds.slice(0, 28) : ds, 234, INK);
    const start = keyOf(p.y, p.m, p.d);
    const nxt = Object.keys(st.notes).filter(k => k >= start).sort()[0];
    if (nxt) textC((nxt.slice(8, 10) + "/" + nxt.slice(5, 7) + " " + fold(st.notes[nxt].txt)).slice(0, 28), 252, SKY);
    const cd = countdown();
    if (cd) textC(cd, 268, LIME);
    const wt = cityName().slice(0, 12) + " " + tempNow() + "C";
    text(wt, 6, 299, SKY);
    battery(296, NIGHT);
  }
  function drawWifi() {
    g.fillStyle = ASPHALT; g.fillRect(0, 0, W, H);
    text("WIFI", 8, 8, YELLOW, 2);
    text("RESEAUX 2,4 GHZ", 8, 32, MUTED);
    ["MAISON", "PHONE"].forEach((n, i) => {
      g.fillStyle = PANEL; g.fillRect(8, 52 + i * 36, 224, 30);
      text(n, 16, 62 + i * 36, WHITE);
      if (st.wifi && i === 0) text("CONNU", 160, 62, LIME);
    });
    text("LA CARTE SE CONNECTE ICI.", 8, 140, MUTED);
    text("CETTE PAGE NE CAPTE PAS", 8, 154, MUTED);
    text("LE WIFI : ELLE MONTRE", 8, 168, MUTED);
    text("SEULEMENT L ECRAN.", 8, 182, MUTED);
    button(8, H - 36, 224, 28, "RETOUR", REDP, CREAM);
  }
  function drawPtr() {
    g.fillStyle = NIGHT; g.fillRect(0, 0, W, H);
    textC("POINTEUR", 16, YELLOW, 2);
    textC("TOUCHE LE CROIX", 48, CREAM);
    const pts = [[20, 80],[200, 80],[120, 160],[20, 240],[200, 240]];
    const t = pts[Math.min(st.ptr, 4)];
    g.strokeStyle = st.ptr > 4 ? LIME : GOLD;
    g.beginPath(); g.moveTo(t[0] - 8, t[1]); g.lineTo(t[0] + 8, t[1]); g.moveTo(t[0], t[1] - 8); g.lineTo(t[0], t[1] + 8); g.stroke();
    textC(st.ptr > 4 ? "OK" : (st.ptr + 1) + " / 5", 270, CREAM);
    textC("TOUCHE POUR CONTINUER", 292, MUTED);
  }
  function drawClock() {
    g.fillStyle = ASPHALT; g.fillRect(0, 0, W, H);
    text("SAISIE", 8, 2, YELLOW);
    const p = parts();
    text(st.field === "h" ? ">" + st.bufH : pad(p.hh) + pad(p.mm) + pad(p.ss), 8, 24, WHITE, 2);
    text(st.field === "d" ? ">" + st.bufD : pad(p.d) + pad(p.m) + p.y, 8, 48, st.field === "d" ? YELLOW : WHITE);
    text("FUSEAU " + (st.field === "z" ? st.bufZ : (st.tz >= 0 ? "+" : "") + st.tz), 8, 64, st.field === "z" ? YELLOW : MUTED);
    st._keys = drawKbd(88, true);
    button(4, H - 26, 74, 22, "HEURE", PANEL, WHITE);
    button(82, H - 26, 74, 22, "DATE", PANEL, WHITE);
    button(160, H - 26, 76, 22, "OK", GREEN, BLACK);
  }

  function ensureFake() {
    if (st.fake) return;
    const p = parts();
    st.fake = {y: p.y, m: p.m, d: p.d, hh: p.hh, mm: p.mm, ss: p.ss};
  }
  function tweak(key, delta) {
    if (key === "tz") { st.tz = clamp(st.tz + delta, -12, 14); st.msg = "FUSEAU " + (st.tz >= 0 ? "+" : "") + st.tz; return; }
    if (key === "vol") { st.vol = clamp(st.vol + delta, 0, 10); st.msg = st.vol ? "VOLUME " + st.vol : "MUET"; return; }
    ensureFake();
    const f = st.fake;
    if (key === "hh") f.hh = (f.hh + delta + 24) % 24;
    else if (key === "mi") f.mm = (f.mm + delta + 60) % 60;
    else if (key === "dd") f.d += delta;
    else if (key === "mo") f.m += delta;
    else if (key === "yy") f.y += delta;
    if (f.m < 1) { f.m = 12; f.y--; }
    if (f.m > 12) { f.m = 1; f.y++; }
    f.y = clamp(f.y, 2024, 2099);
    f.d = clamp(f.d, 1, dim(f.y, f.m));
    st.vy = f.y; st.vm = f.m; st.sel = [f.y, f.m, f.d];
    st.msg = "HEURE REGLEE";
    if (opt.onClock) opt.onClock();
  }

  function saveNotes() { store.save("cg-notes", st.notes); }
  function saveRec() { store.save("cg-rec", st.rec); }

  function openNote(sel) {
    st.sel = sel;
    st.edit = keyOf(sel[0], sel[1], sel[2]);
    const n = st.notes[st.edit] || {};
    st.buf = n.txt || "";
    st.theme = n.t || "anniv";
    st.num = false;
    mode = "note";
  }
  function saveNote() {
    const txt = st.buf.trim();
    if (!txt) delete st.notes[st.edit];
    else st.notes[st.edit] = {t: st.theme, txt};
    saveNotes();
    mode = "cal";
  }

  function bootGame(day) {
    const played = st.rec.played || [];
    if (!played.includes(day)) { played.push(day); st.rec.played = played; saveRec(); }
    game = makeGame(day);
    mode = "play";
    st.idle = performance.now();
  }
  function openGift(day) {
    st.gift = day;
    st.sel = [st.vy, 12, day];
    mode = "gift";
  }

  function go(next) {
    if (next === "jeu") { mode = "jeu"; st.idle = performance.now(); ping(); return; }
    if (next === "set") { mode = "set"; return; }
    mode = next;
    st.idle = performance.now();
    ping();
  }
  function ping() { if (opt.onMode) opt.onMode(mode === "play" || mode === "gift" || mode === "locked" ? "jeu" : mode, st.day); }

  function tapUI(x, y) {
    if (mode === "saver") { mode = st.saverFrom; st.idle = performance.now(); return; }
    if (mode === "locked") { mode = "jeu"; ping(); return; }
    if (mode === "ptr") {
      st.ptr++;
      if (st.ptr > 5) { mode = "set"; st.msg = "POINTEUR OK"; }
      return;
    }
    if (mode === "wifi") { if (y > H - 40) { st.wifi = true; mode = "set"; st.msg = "WIFI DEMO"; } return; }
    if (mode === "clock") return tapClock(x, y);
    if (mode === "gift") return tapGift(x, y);
    if (mode === "city") return tapCity(x, y);
    if (mode === "note") return tapNote(x, y);
    if (mode === "jeu") return tapJeu(x, y);
    if (mode === "cal" || mode === "meteo" || mode === "set") {
      const tab = tabAt(x, y);
      if (tab) { go(tab); return; }
    }
    if (mode === "cal") return tapCal(x, y);
    if (mode === "meteo") return tapMeteo(x, y);
    if (mode === "set") return tapSet(x, y);
  }
  function tapCal(x, y) {
    if (y < 26) {
      if (x < 24) shiftMonth(-1);
      else if (x >= 104 && x < 128) shiftMonth(1);
      else if (x < 104) {
        const p = parts();
        st.vy = p.y; st.vm = p.m; st.sel = [p.y, p.m, p.d];
      }
      return;
    }
    if (y >= 236 && y < 278) {
      const p = parts(), start = keyOf(p.y, p.m, p.d);
      const ev = Object.keys(st.notes).filter(k => k >= start).sort();
      const i = (y - 236) / 12 | 0;
      if (ev[i]) openNote([+ev[i].slice(0, 4), +ev[i].slice(5, 7), +ev[i].slice(8, 10)]);
      return;
    }
    if (y >= 37 && y < 37 + 6 * 31) {
      const col = x / 34 | 0, row = (y - 37) / 31 | 0;
      if (col < 0 || col > 6) return;
      const first = dowMon(st.vy, st.vm, 1), day = row * 7 + col - first + 1;
      if (day < 1 || day > dim(st.vy, st.vm)) return;
      const picked = [st.vy, st.vm, day];
      if (st.sel && st.sel[0] === picked[0] && st.sel[1] === picked[1] && st.sel[2] === picked[2]) {
        if (st.vm === 12 && day <= 25 && unlocked(day)) openGift(day);
        else openNote(picked);
      } else st.sel = picked;
    }
  }
  function shiftMonth(delta) {
    let m = st.vm + delta, y = st.vy;
    if (m < 1) { m = 12; y--; } else if (m > 12) { m = 1; y++; }
    st.vy = y; st.vm = m;
    let d = st.sel ? st.sel[2] : 1;
    if (d > dim(y, m)) d = dim(y, m);
    st.sel = [y, m, d];
  }
  function tapMeteo(x, y) {
    if (y >= 92 && y < 116) {
      if (x < 112) mode = "city";
      else { st.msg = "MAJ " + pad(parts().hh) + ":" + pad(parts().mm); if (opt.onCity) opt.onCity(st.city); }
    }
  }
  function tapSet(x, y) {
    const rows = ["hh","mi","dd","mo","yy","tz","vol"];
    for (let i = 0; i < rows.length; i++) {
      const yy = 2 + i * 22;
      if (y >= yy && y < yy + 20) {
        if (x >= 140 && x < 180) tweak(rows[i], -1);
        else if (x >= 186) tweak(rows[i], 1);
        else if (rows[i] !== "vol") { st.field = rows[i] === "tz" ? "z" : (rows[i] === "hh" || rows[i] === "mi" ? "h" : "d"); openClock(); }
        return;
      }
    }
    const yy = 2 + 7 * 22;
    if (y >= yy && y < yy + 26) {
      if (x < 120) { st.fake = null; st.msg = "HEURE OK"; const p = parts(); st.vy = p.y; st.vm = p.m; st.sel = [p.y, p.m, p.d]; if (opt.onClock) opt.onClock(); }
      else { mode = "wifi"; }
      return;
    }
    if (y >= 210 && y < 238) openClock();
    else if (y >= 244 && y < 276) { st.ptr = 0; mode = "ptr"; }
  }
  function openClock() {
    const p = parts();
    st.bufH = pad(p.hh) + pad(p.mm) + pad(p.ss);
    st.bufD = pad(p.d) + pad(p.m) + p.y;
    st.bufZ = (st.tz >= 0 ? "+" : "") + st.tz;
    if (st.field !== "h" && st.field !== "d" && st.field !== "z") st.field = "h";
    mode = "clock";
  }
  function tapClock(x, y) {
    if (y >= H - 26) {
      if (x < 80) st.field = "h";
      else if (x < 156) st.field = "d";
      else {
        if (st.field === "h" && st.bufH.length >= 4) {
          ensureFake();
          st.fake.hh = clamp(+st.bufH.slice(0, 2), 0, 23);
          st.fake.mm = clamp(+st.bufH.slice(2, 4), 0, 59);
          st.fake.ss = clamp(+(st.bufH.slice(4, 6) || "0"), 0, 59);
        }
        if (st.field === "d" && st.bufD.length >= 4) {
          ensureFake();
          st.fake.d = clamp(+st.bufD.slice(0, 2), 1, 31);
          st.fake.m = clamp(+st.bufD.slice(2, 4), 1, 12);
          if (st.bufD.length >= 8) st.fake.y = clamp(+st.bufD.slice(4, 8), 2024, 2099);
          st.fake.d = clamp(st.fake.d, 1, dim(st.fake.y, st.fake.m));
          st.vy = st.fake.y; st.vm = st.fake.m; st.sel = [st.fake.y, st.fake.m, st.fake.d];
        }
        if (st.field === "z" && st.bufZ) st.tz = clamp(parseInt(st.bufZ, 10) || 0, -12, 14);
        st.msg = "HEURE REGLEE";
        mode = "set";
        if (opt.onClock) opt.onClock();
      }
      return;
    }
    const k = (st._keys || []).find(b => hit(x, y, b[1], b[2], b[3], b[4]));
    if (!k) return;
    const ch = k[0];
    if (ch === "BS") {
      if (st.field === "h") st.bufH = st.bufH.slice(0, -1);
      else if (st.field === "d") st.bufD = st.bufD.slice(0, -1);
      else st.bufZ = st.bufZ.slice(0, -1);
      return;
    }
    if (!/\d/.test(ch) && !(st.field === "z" && (ch === "+" || ch === "-"))) return;
    if (st.field === "h" && st.bufH.length < 6) st.bufH += ch;
    else if (st.field === "d" && st.bufD.length < 8) st.bufD += ch;
    else if (st.field === "z" && st.bufZ.length < 3) st.bufZ += ch;
  }
  function tapNote(x, y) {
    if (y >= 14 && y < 52) { st.theme = THEMES[Math.min(4, x / 48 | 0)][0]; return; }
    if (y >= H - 26) {
      if (x < 76) { delete st.notes[st.edit]; saveNotes(); mode = "cal"; }
      else if (x < 150) st.num = !st.num;
      else saveNote();
      return;
    }
    const k = (st._keys || []).find(b => hit(x, y, b[1], b[2], b[3], b[4]));
    if (!k) return;
    if (k[0] === "SH") { st.low = !st.low; return; }
    if (k[0] === "BS") st.buf = st.buf.slice(0, -1);
    else if (st.buf.length < 60) st.buf += k[0];
  }
  function tapJeu(x, y) {
    if (y < 42) return;
    if (y >= 292) { mode = "cal"; ping(); return; }
    for (let day = 1; day <= 25; day++) {
      const r = (day - 1) / 5 | 0, c = (day - 1) % 5;
      const bx = 5 + c * 46, by = 46 + r * 48;
      if (hit(x, y, bx, by, 42, 44, 1)) {
        st.day = day;
        if (unlocked(day)) bootGame(day);
        break;
      }
    }
  }
  function tapGift(x, y) {
    if (hit(x, y, 194, 58, 28, 22, 8)) { mode = "cal"; return; }
    if (hit(x, y, 134, 238, 80, 22, 4) || hit(x, y, 70, 100, 100, 80)) { bootGame(st.gift); return; }
    if (hit(x, y, 26, 238, 80, 22, 4)) { openNote([st.vy, 12, st.gift]); }
  }
  function drawCity() {
    g.fillStyle = ASPHALT; g.fillRect(0, 0, W, H);
    text("VILLE", 8, 8, YELLOW, 2);
    text("CHOISIS TA VILLE", 8, 32, MUTED);
    (opt.cities || []).slice(0, 8).forEach((c, i) => {
      const y = 52 + i * 28;
      g.fillStyle = i === st.city ? YELLOW : PANEL;
      g.fillRect(8, y, 224, 24);
      text(fold(c[1]).slice(0, 16), 16, y + 8, i === st.city ? BLACK : WHITE);
    });
    button(8, H - 36, 224, 28, "RETOUR", REDP, CREAM);
  }
  function tapCity(x, y) {
    if (y > H - 40) { mode = "meteo"; return; }
    const i = (y - 52) / 28 | 0;
    if (i >= 0 && i < (opt.cities || []).length && y >= 52) {
      st.city = i;
      st.msg = "VILLE " + cityName();
      mode = "meteo";
      if (opt.onCity) opt.onCity(i);
    }
  }

  function hud(gm) {
    g.fillStyle = SLATE; g.fillRect(0, 0, W, HUD);
    menuBtn();
    const s = pad(Math.min(gm.score, 999999), 6);
    text(s, 56, 6, CREAM);
    text("HI", 112, 6, CREAM);
    text(pad(Math.min(gm.record, 999999), 6), 130, 6, GREY);
    for (let i = 0; i < Math.max(0, Math.min(gm.lives, 5)); i++) {
      const x = 232 - (i + 1) * 10, y = 6;
      g.fillStyle = RED;
      g.fillRect(x, y + 2, 3, 3); g.fillRect(x + 4, y + 2, 3, 3); g.fillRect(x, y + 4, 7, 3); g.fillRect(x + 1, y + 7, 5, 2); g.fillRect(x + 2, y + 9, 3, 2);
    }
  }
  function drawTitle(gm) {
    g.fillStyle = SLATE; g.fillRect(0, 0, W, H);
    menuBtn();
    text("JOUR " + gm.day, 176, 6, CREAM);
    bands(26);
    const name = gm.title, scale = name.length <= 9 ? 3 : 2, y = scale === 3 ? 52 : 56;
    textC(name, y, CREAM, scale, REDP);
    (gm.help || []).slice(0, 3).forEach((line, i) => textC(line, 206 + i * 12, i ? CYAN : WHITE));
    textC("RECORD " + pad(gm.record, 6), 250, CREAM);
    g.fillStyle = REDP; g.fillRect(0, 296, W, 2);
    if ((gm.blink | 0) % 2 === 0) textC("TOUCHE POUR JOUER", 274, CREAM);
  }
  function drawOver(gm) {
    g.fillStyle = SLATE; g.fillRect(14, 92, 212, 164);
    g.strokeStyle = TEAL; g.strokeRect(14.5, 92.5, 211, 163);
    g.strokeStyle = REDP; g.strokeRect(16.5, 94.5, 207, 159);
    textC(gm.result || "GAME OVER", 104, REDP, 2, TEAL);
    textC("SCORE", 132, CREAM);
    textC(pad(Math.min(gm.score, 999999), 6), 146, CREAM, 2, REDP);
    textC(gm.newRec ? "NOUVEAU RECORD !" : "RECORD " + pad(gm.record, 6), 186, gm.newRec ? CREAM : GREY);
    textC("TOUCHE : REJOUER", 222, CREAM);
    textC("MENU : QUITTER", 236, CREAM);
  }
  function finish(gm, result) {
    gm.result = result || "GAME OVER";
    gm.phase = "over";
    gm.newRec = gm.score > gm.record;
    if (gm.newRec) { gm.record = gm.score; st.rec[String(gm.day)] = gm.score; saveRec(); }
  }
  function hurt(gm) {
    gm.lives--;
    if (gm.lives <= 0) finish(gm);
    else gm.reset();
  }

  function makeGame(day) {
    const gm = {day, title: TITLES[day], help: HELP[day], score: 0, lives: day === 4 ? 1 : 3, record: st.rec[String(day)] || 0, phase: "title", blink: 0, result: ""};
    const spec = SPECS[day];
    spec.init(gm);
    gm.reset = () => spec.init(gm);
    gm.step = (dt, p) => spec.step(gm, dt, p);
    gm.paint = () => spec.paint(gm);
    return gm;
  }
  function runGame(dt, p) {
    const gm = game;
    gm.blink += dt * 2;
    if (p.tap && p.y < HUD + 4 && p.x < 56) { mode = "jeu"; game = null; ping(); return; }
    if (gm.phase === "title") { if (p.tap) { gm.phase = "play"; gm.reset(); } return; }
    if (gm.phase === "over") {
      if (p.tap) { gm.phase = "play"; gm.score = 0; gm.lives = gm.day === 4 ? 1 : 3; gm.reset(); }
      return;
    }
    const r = gm.step(dt, p);
    if (r === "dead") hurt(gm);
    else if (r === "win") finish(gm, "GAGNE");
    else if (r === "lose") finish(gm, "PERDU");
  }

  const COLS = ["#FF3EA5","#FF8A1F","#FFD23F","#3CFF7A","#3BE3FF","#9B6BFF"];
  const SPECS = {
    1: {
      init(gm) {
        gm.px = 120; gm.ball = {x: 120, y: 250, vx: 80, vy: -170};
        gm.bricks = [];
        for (let r = 0; r < 6; r++) for (let c = 0; c < 8; c++) gm.bricks.push({x: 16 + c * 26, y: 36 + r * 12, on: 1, col: COLS[r]});
      },
      step(gm, dt, p) {
        if (p.down) gm.px = clamp(p.x, 28, 212);
        const b = gm.ball;
        b.x += b.vx * dt; b.y += b.vy * dt;
        if (b.x < 10 || b.x > 230) b.vx *= -1;
        if (b.y < 28) b.vy = Math.abs(b.vy);
        if (b.vy > 0 && b.y > 286 && b.y < 302 && Math.abs(b.x - gm.px) < 26) { b.vy = -Math.abs(b.vy); b.vx = (b.x - gm.px) * 5; }
        for (const br of gm.bricks) if (br.on && b.x > br.x && b.x < br.x + 24 && b.y > br.y && b.y < br.y + 12) { br.on = 0; b.vy *= -1; gm.score += 10; break; }
        if (!gm.bricks.some(br => br.on)) { gm.score += 50; this.init(gm); gm.score -= 0; }
        if (b.y > 318) return "dead";
      },
      paint(gm) {
        g.fillStyle = "#0A0A20"; g.fillRect(0, HUD, W, H - HUD);
        gm.bricks.forEach(br => { if (!br.on) return; g.fillStyle = br.col; g.fillRect(br.x, br.y, 24, 10); });
        g.fillStyle = CYAN; g.fillRect(gm.px - 22, 292, 44, 8);
        g.fillStyle = WHITE; g.fillRect(gm.ball.x - 3, gm.ball.y - 3, 6, 6);
      }
    },
    2: shooter(false),
    24: shooter(true),
    3: {
      init(gm) {
        gm.body = [{x: 6, y: 12},{x: 5, y: 12},{x: 4, y: 12}]; gm.dir = {x: 1, y: 0}; gm.acc = 0;
        gm.food = {x: 12, y: 8};
      },
      step(gm, dt, p) {
        gm.acc += dt;
        if (gm.acc < 0.12) return;
        gm.acc = 0;
        const hd = gm.body[0];
        let dir = gm.dir;
        if (p.down) {
          const tx = clamp(p.x / 12 | 0, 0, 19), ty = clamp((p.y - 24) / 12 | 0, 0, 23);
          const opts = [dir, {x: dir.y, y: -dir.x}, {x: -dir.y, y: dir.x}];
          let best = 1e9;
          opts.forEach(d => {
            const nx = hd.x + d.x, ny = hd.y + d.y;
            if (nx < 0 || ny < 0 || nx > 19 || ny > 23) return;
            if (gm.body.some(s => s.x === nx && s.y === ny)) return;
            const sc = Math.abs(nx - tx) + Math.abs(ny - ty);
            if (sc < best) { best = sc; dir = d; }
          });
        }
        gm.dir = dir;
        const nx = hd.x + dir.x, ny = hd.y + dir.y;
        if (nx < 0 || ny < 0 || nx > 19 || ny > 23 || gm.body.some(s => s.x === nx && s.y === ny)) return "dead";
        gm.body.unshift({x: nx, y: ny});
        if (nx === gm.food.x && ny === gm.food.y) {
          gm.score += 10;
          do gm.food = {x: Math.random() * 20 | 0, y: Math.random() * 24 | 0}; while (gm.body.some(s => s.x === gm.food.x && s.y === gm.food.y));
        } else gm.body.pop();
      },
      paint(gm) {
        g.fillStyle = NIGHT; g.fillRect(0, HUD, W, H - HUD);
        g.fillStyle = PINK; g.fillRect(gm.food.x * 12 + 2, 24 + gm.food.y * 12 + 2, 8, 8);
        gm.body.forEach((s, i) => { g.fillStyle = i ? LIME : GOLD; g.fillRect(s.x * 12 + 1, 24 + s.y * 12 + 1, 10, 10); });
      }
    },
    4: {
      init(gm) { gm.me = 120; gm.cpu = 120; gm.ball = {x: 120, y: 160, vx: 0, vy: 150}; gm.pts = [0, 0]; },
      step(gm, dt, p) {
        if (p.down) gm.me = clamp(p.x, 24, 216);
        gm.cpu += clamp(gm.ball.x - gm.cpu, -140 * dt, 140 * dt);
        const b = gm.ball;
        b.x += b.vx * dt; b.y += b.vy * dt;
        if (b.x < 8 || b.x > 232) b.vx *= -1;
        if (b.vy > 0 && b.y > 286 && b.y < 300 && Math.abs(b.x - gm.me) < 28) { b.vy = -Math.abs(b.vy) * 1.04; b.vx = (b.x - gm.me) * 4; }
        if (b.vy < 0 && b.y < 48 && b.y > 34 && Math.abs(b.x - gm.cpu) < 28) { b.vy = Math.abs(b.vy) * 1.04; b.vx = (b.x - gm.cpu) * 4; }
        if (b.y > 318) { gm.pts[0]++; b.x = 120; b.y = 160; b.vy = 150; b.vx = 0; }
        if (b.y < 22) { gm.pts[1]++; gm.score = gm.pts[1]; b.x = 120; b.y = 160; b.vy = -150; b.vx = 0; }
        if (gm.pts[1] >= 7) return "win";
        if (gm.pts[0] >= 7) return "lose";
      },
      paint(gm) {
        g.fillStyle = "#0A0A14"; g.fillRect(0, HUD, W, H - HUD);
        text(String(gm.pts[0]), 80, 28, PINK, 2);
        text(String(gm.pts[1]), 140, 28, CYAN, 2);
        text("IA", 80, 50, GREY); text("TOI", 132, 50, GREY);
        g.fillStyle = PINK; g.fillRect(gm.cpu - 22, 36, 44, 8);
        g.fillStyle = CYAN; g.fillRect(gm.me - 22, 292, 44, 8);
        g.fillStyle = GOLD; g.fillRect(gm.ball.x - 4, gm.ball.y - 4, 8, 8);
      }
    },
    5: {
      init(gm) {
        gm.x = 120; gm.miss = null; gm.aliens = [];
        for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) gm.aliens.push({x: 28 + c * 32, y: 40 + r * 22, on: 1});
        gm.dir = 18; gm.acc = 0;
      },
      step(gm, dt, p) {
        if (p.down) gm.x = clamp(p.x, 16, 224);
        if (p.down && !gm.miss) gm.miss = {x: gm.x, y: 286};
        if (gm.miss) { gm.miss.y -= 220 * dt; if (gm.miss.y < 28) gm.miss = null; }
        gm.acc += dt;
        if (gm.acc > 0.45) {
          gm.acc = 0;
          let edge = false;
          gm.aliens.forEach(a => { if (!a.on) return; a.x += gm.dir; if (a.x < 10 || a.x > 214) edge = true; });
          if (edge) { gm.dir *= -1; gm.aliens.forEach(a => { if (a.on) a.y += 10; }); }
        }
        if (gm.miss) gm.aliens.forEach(a => {
          if (a.on && Math.abs(gm.miss.x - a.x) < 12 && Math.abs(gm.miss.y - a.y) < 8) { a.on = 0; gm.miss = null; gm.score += 20; }
        });
        if (gm.aliens.some(a => a.on && a.y > 270)) return "dead";
        if (!gm.aliens.some(a => a.on)) { gm.score += 100; this.init(gm); }
      },
      paint(gm) {
        g.fillStyle = "#060814"; g.fillRect(0, HUD, W, H - HUD);
        gm.aliens.forEach(a => { if (!a.on) return; g.fillStyle = LIME; g.fillRect(a.x - 8, a.y - 4, 16, 8); });
        g.fillStyle = CYAN; g.fillRect(gm.x - 12, 292, 24, 8);
        if (gm.miss) { g.fillStyle = GOLD; g.fillRect(gm.miss.x - 1, gm.miss.y, 2, 8); }
      }
    },
    6: {
      init(gm) { gm.ang = -1.2; gm.rocks = [{x: 40, y: 60, vx: 30, vy: 20, r: 16},{x: 180, y: 90, vx: -24, vy: 28, r: 14},{x: 120, y: 50, vx: 18, vy: 36, r: 12}]; gm.shots = []; gm.cd = 0; },
      step(gm, dt, p) {
        if (p.down) gm.ang = Math.atan2(p.y - 180, p.x - 120);
        gm.cd -= dt;
        if (p.down && gm.cd <= 0) { gm.shots.push({x: 120, y: 180, vx: Math.cos(gm.ang) * 180, vy: Math.sin(gm.ang) * 180}); gm.cd = 0.28; }
        gm.shots.forEach(s => { s.x += s.vx * dt; s.y += s.vy * dt; });
        gm.shots = gm.shots.filter(s => s.x > 0 && s.x < W && s.y > 20 && s.y < H);
        gm.rocks.forEach(rk => {
          rk.x += rk.vx * dt; rk.y += rk.vy * dt;
          if (rk.x < rk.r || rk.x > W - rk.r) rk.vx *= -1;
          if (rk.y < 24 + rk.r || rk.y > H - rk.r) rk.vy *= -1;
          if (Math.hypot(rk.x - 120, rk.y - 180) < rk.r + 8) rk.hit = 1;
        });
        gm.shots.forEach(s => gm.rocks.forEach(rk => {
          if (!rk.dead && Math.hypot(s.x - rk.x, s.y - rk.y) < rk.r) {
            rk.dead = 1; s.dead = 1; gm.score += 15;
            if (rk.r > 8) { gm.rocks.push({x: rk.x, y: rk.y, vx: -rk.vy, vy: rk.vx, r: rk.r - 5}); gm.rocks.push({x: rk.x, y: rk.y, vx: rk.vy, vy: -rk.vx, r: rk.r - 5}); }
          }
        }));
        gm.rocks = gm.rocks.filter(rk => !rk.dead);
        gm.shots = gm.shots.filter(s => !s.dead);
        if (gm.rocks.some(rk => rk.hit)) return "dead";
        if (!gm.rocks.length) { gm.score += 50; this.init(gm); }
      },
      paint(gm) {
        g.fillStyle = "#0A1020"; g.fillRect(0, HUD, W, H - HUD);
        gm.rocks.forEach(rk => { g.strokeStyle = GREY; g.strokeRect(rk.x - rk.r, rk.y - rk.r, rk.r * 2, rk.r * 2); });
        g.strokeStyle = GOLD; g.beginPath(); g.moveTo(120, 180); g.lineTo(120 + Math.cos(gm.ang) * 28, 180 + Math.sin(gm.ang) * 28); g.stroke();
        g.fillStyle = CYAN; g.fillRect(112, 172, 16, 16);
        g.fillStyle = GOLD; gm.shots.forEach(s => g.fillRect(s.x, s.y, 3, 3));
      }
    },
    7: {
      init(gm) { gm.y = 280; gm.cars = []; gm.t = 0; },
      step(gm, dt, p) {
        gm.t += dt;
        if (p.tap) gm.y += p.y < gm.y ? -28 : 28;
        gm.y = clamp(gm.y, 36, 300);
        if (Math.random() < dt * 1.4) {
          const lane = Math.random() < .5 ? 48 : 150;
          gm.cars.push({x: lane, y: Math.random() < .5 ? -20 : 330, vy: (Math.random() < .5 ? 1 : -1) * (50 + Math.random() * 40)});
        }
        gm.cars.forEach(c => c.y += c.vy * dt);
        gm.cars = gm.cars.filter(c => c.y > -30 && c.y < 340);
        if (gm.y > 55 && gm.y < 250 && gm.cars.some(c => Math.abs(c.y - gm.y) < 16 && Math.abs(c.x + 16 - 120) < 24)) return "dead";
        if (gm.y < 48) { gm.score += 25; gm.y = 280; }
      },
      paint(gm) {
        g.fillStyle = "#1A4030"; g.fillRect(0, HUD, W, H - HUD);
        g.fillStyle = "#3A3A44"; g.fillRect(50, 40, 150, 240);
        g.fillStyle = GOLD; for (let y = 50; y < 270; y += 18) g.fillRect(118, y, 4, 8);
        gm.cars.forEach(c => { g.fillStyle = c.vy > 0 ? "#3C7CFF" : ORANGE; g.fillRect(c.x, c.y, 26, 16); });
        g.fillStyle = YELLOW; g.fillRect(114, gm.y - 6, 12, 12);
      }
    },
    8: faller(false),
    21: faller(true),
    9: {
      init(gm) { gm.x = 120; gm.cars = []; gm.road = 0; gm.t = 0; },
      step(gm, dt, p) {
        gm.t += dt; gm.road = (gm.road + 180 * dt) % 32;
        if (p.down) gm.x += clamp(p.x - gm.x, -160 * dt, 160 * dt);
        gm.x = clamp(gm.x, 48, 192);
        if (Math.random() < dt * 1.3) gm.cars.push({x: 56 + (Math.random() * 3 | 0) * 44, y: 10, vy: 70 + Math.random() * 50});
        gm.cars.forEach(c => c.y += c.vy * dt);
        gm.cars = gm.cars.filter(c => c.y < 340);
        if (gm.cars.some(c => c.y > 230 && c.y < 280 && Math.abs(c.x - gm.x) < 22)) return "dead";
        gm.score += dt * 10 | 0;
      },
      paint(gm) {
        g.fillStyle = "#288C32"; g.fillRect(0, HUD, W, H - HUD);
        g.fillStyle = "#3C3C46"; g.fillRect(36, HUD, 168, H - HUD);
        g.fillStyle = "#E23C3C"; g.fillRect(36, HUD, 4, H); g.fillRect(200, HUD, 4, H);
        g.fillStyle = WHITE;
        for (let y = -32 + gm.road; y < H; y += 32) { g.fillRect(78, y, 4, 14); g.fillRect(122, y, 4, 14); g.fillRect(166, y, 4, 14); }
        gm.cars.forEach(c => { g.fillStyle = "#6E3CDC"; g.fillRect(c.x - 10, c.y, 20, 28); });
        g.fillStyle = "#E62828"; g.fillRect(gm.x - 10, 250, 20, 28);
      }
    },
    10: {
      init(gm) { gm.y = 160; gm.x = 70; gm.walls = []; gm.t = 0; },
      step(gm, dt, p) {
        gm.t += dt;
        gm.y += (p.down ? -90 : 70) * dt;
        if (gm.y < 28 || gm.y > 300) return "dead";
        if (Math.random() < dt * 1.6) gm.walls.push({x: 250, gap: 70 + Math.random() * 140});
        gm.walls.forEach(w => w.x -= 80 * dt);
        gm.walls = gm.walls.filter(w => w.x > -20);
        if (gm.walls.some(w => Math.abs(w.x - gm.x) < 12 && (gm.y < w.gap || gm.y > w.gap + 70))) return "dead";
        gm.score += dt * 8 | 0;
      },
      paint(gm) {
        g.fillStyle = "#10243A"; g.fillRect(0, HUD, W, H - HUD);
        g.fillStyle = "#2A6A38";
        gm.walls.forEach(w => { g.fillRect(w.x, HUD, 16, w.gap - HUD); g.fillRect(w.x, w.gap + 70, 16, H - w.gap - 70); });
        g.fillStyle = GOLD; g.fillRect(gm.x - 10, gm.y - 4, 20, 8);
        g.fillStyle = CYAN; g.fillRect(gm.x + 8, gm.y - 2, 8, 3);
      }
    },
    11: {
      init(gm) {
        const icons = ["A","B","C","D","E","F","G","H"];
        const deck = icons.concat(icons).sort(() => Math.random() - .5);
        gm.cards = deck.map(v => ({v, up: false, done: false}));
        gm.pick = -1; gm.t = 45; gm.lock = 0;
      },
      step(gm, dt, p) {
        gm.t -= dt;
        if (gm.t <= 0) return "lose";
        if (gm.lock > 0) { gm.lock -= dt; if (gm.lock <= 0 && gm.pick >= 0) { const a = gm.cards[gm.open0], b = gm.cards[gm.pick]; if (a && b && a.v !== b.v) { a.up = b.up = false; } gm.pick = -1; } return; }
        if (!p.tap) return;
        const i = cardAt(p.x, p.y);
        if (i < 0 || gm.cards[i].done || gm.cards[i].up) return;
        gm.cards[i].up = true;
        if (gm.pick < 0) gm.pick = i;
        else {
          const a = gm.cards[gm.pick];
          if (a.v === gm.cards[i].v) { a.done = gm.cards[i].done = true; gm.score += 20; gm.pick = -1; if (gm.cards.every(c => c.done)) return "win"; }
          else { gm.open0 = gm.pick; gm.pick = i; gm.lock = 0.6; }
        }
      },
      paint(gm) {
        g.fillStyle = NIGHT; g.fillRect(0, HUD, W, H - HUD);
        text("TEMPS " + Math.max(0, gm.t | 0), 8, 26, GOLD);
        gm.cards.forEach((c, i) => {
          const x = 12 + (i % 4) * 56, y = 48 + (i / 4 | 0) * 64;
          g.fillStyle = c.done ? TEAL : (c.up ? PANEL : REDP);
          g.fillRect(x, y, 48, 56);
          if (c.up || c.done) text(c.v, x + 20, y + 24, GOLD);
        });
      }
    },
    12: {
      init(gm) {
        gm.grid = Array.from({length: 16}, () => Array(8).fill(0));
        gm.piece = randPiece(); gm.x = 3; gm.y = 0; gm.rot = 0; gm.drop = 0; gm.soft = 0;
      },
      step(gm, dt, p) {
        gm.drop += dt;
        if (p.tap) {
          if (p.y > 268) {
            if (p.x < 80) { if (fit(gm, gm.x - 1, gm.y, gm.rot)) gm.x--; }
            else if (p.x < 160) { const nr = (gm.rot + 1) % 4; if (fit(gm, gm.x, gm.y, nr)) gm.rot = nr; }
            else {
              if (performance.now() - gm.soft < 400) while (fit(gm, gm.x, gm.y + 1, gm.rot)) gm.y++;
              else if (fit(gm, gm.x, gm.y + 1, gm.rot)) gm.y++;
              gm.soft = performance.now();
            }
          }
        }
        if (gm.drop > 0.55) {
          gm.drop = 0;
          if (fit(gm, gm.x, gm.y + 1, gm.rot)) gm.y++;
          else { lockPiece(gm); const n = clearLines(gm); gm.score += [0, 40, 100, 300, 800][n] || 0; gm.piece = randPiece(); gm.x = 3; gm.y = 0; gm.rot = 0; if (!fit(gm, gm.x, gm.y, gm.rot)) return "dead"; }
        }
      },
      paint(gm) {
        g.fillStyle = "#12081C"; g.fillRect(0, HUD, W, H - HUD);
        const ox = 28, oy = 28;
        for (let y = 0; y < 16; y++) for (let x = 0; x < 8; x++) if (gm.grid[y][x]) { g.fillStyle = COLS[gm.grid[y][x] % 6]; g.fillRect(ox + x * 14, oy + y * 14, 13, 13); }
        pieceCells(gm.piece, gm.rot).forEach(c => { g.fillStyle = COLS[gm.piece]; g.fillRect(ox + (gm.x + c[0]) * 14, oy + (gm.y + c[1]) * 14, 13, 13); });
        button(8, 272, 68, 36, "<", VIOLET, WHITE);
        button(86, 272, 68, 36, "TOURNE", VIOLET, WHITE);
        button(164, 272, 68, 36, "BAS", VIOLET, WHITE);
      }
    },
    13: {
      init(gm) { gm.birds = []; gm.t = 0; },
      step(gm, dt, p) {
        gm.t += dt;
        if (gm.birds.length < 3 && Math.random() < dt * 1.2) gm.birds.push({x: 20 + Math.random() * 180, y: 40 + Math.random() * 180, hp: 3, fly: 0});
        gm.birds.forEach(b => { if (b.fly) { b.y -= 80 * dt; b.x += 30 * dt; } });
        if (p.tap) {
          const b = gm.birds.find(b => !b.fly && Math.abs(p.x - b.x) < 16 && Math.abs(p.y - b.y) < 14);
          if (b) { b.hp--; gm.score += 5; if (b.hp <= 0) { b.dead = 1; gm.score += 15; } }
        }
        gm.birds.forEach(b => { if (!b.fly && !b.dead && gm.t > 0 && b.hp === 3 && Math.random() < dt * 0.15) b.fly = 1; });
        if (gm.birds.some(b => b.fly && b.y < 24)) return "dead";
        gm.birds = gm.birds.filter(b => !b.dead && b.y > 0);
      },
      paint(gm) {
        g.fillStyle = "#14304A"; g.fillRect(0, HUD, W, H - HUD);
        gm.birds.forEach(b => { g.fillStyle = b.fly ? GREY : GOLD; g.fillRect(b.x - 10, b.y - 6, 20, 12); text(String(b.hp), b.x - 4, b.y - 4, BLACK); });
      }
    },
    14: {
      init(gm) { gm.y = 160; gm.shots = []; gm.foes = []; gm.men = [{y: 80},{y: 140},{y: 200},{y: 250}]; gm.cd = 0; },
      step(gm, dt, p) {
        if (p.down) gm.y = clamp(p.y, 36, 300);
        gm.cd -= dt;
        if (p.down && gm.cd <= 0) { gm.shots.push({x: 28, y: gm.y}); gm.cd = 0.35; }
        if (Math.random() < dt * 0.7) gm.foes.push({x: 230, y: 50 + Math.random() * 220, vy: 0});
        gm.shots.forEach(s => s.x += 200 * dt);
        gm.foes.forEach(f => { f.x -= 40 * dt; const m = gm.men.find(m => !m.gone && Math.abs(m.y - f.y) < 16); if (m && f.x < 40) m.gone = 1; });
        gm.shots.forEach(s => gm.foes.forEach(f => { if (!f.dead && Math.abs(s.x - f.x) < 10 && Math.abs(s.y - f.y) < 10) { f.dead = s.dead = 1; gm.score += 25; } }));
        gm.shots = gm.shots.filter(s => !s.dead && s.x < W);
        gm.foes = gm.foes.filter(f => !f.dead && f.x > -10);
        if (gm.men.every(m => m.gone)) return "dead";
      },
      paint(gm) {
        g.fillStyle = "#101820"; g.fillRect(0, HUD, W, H - HUD);
        gm.men.forEach(m => { if (m.gone) return; g.fillStyle = CREAM; g.fillRect(8, m.y, 6, 12); });
        g.fillStyle = CYAN; g.fillRect(18, gm.y - 6, 16, 12);
        gm.foes.forEach(f => { g.fillStyle = REDP; g.fillRect(f.x, f.y - 6, 14, 10); });
        g.fillStyle = GOLD; gm.shots.forEach(s => g.fillRect(s.x, s.y, 6, 2));
      }
    },
    15: {
      init(gm) {
        gm.map = Array.from({length: 12}, (_, y) => Array.from({length: 10}, (_, x) => (x === 0 || y === 0 || x === 9 || y === 11) ? 1 : (Math.random() < .18 ? 2 : 0)));
        gm.px = 2; gm.py = 2; gm.diam = 6; gm.got = 0; gm.acc = 0;
        for (let i = 0; i < gm.diam; i++) gm.map[1 + (Math.random() * 9 | 0)][1 + (Math.random() * 7 | 0)] = 3;
        gm.map[10][8] = 4;
      },
      step(gm, dt, p) {
        gm.acc += dt;
        if (!p.down || gm.acc < 0.18) return;
        gm.acc = 0;
        const tx = clamp(p.x / 24 | 0, 0, 9), ty = clamp((p.y - 24) / 22 | 0, 0, 11);
        const dx = Math.sign(tx - gm.px), dy = Math.sign(ty - gm.py);
        const nx = gm.px + (Math.abs(tx - gm.px) > Math.abs(ty - gm.py) ? dx : 0);
        const ny = gm.py + (Math.abs(tx - gm.px) > Math.abs(ty - gm.py) ? 0 : dy);
        if (ny < 0 || nx < 0 || ny > 11 || nx > 9) return;
        const cell = gm.map[ny][nx];
        if (cell === 1) return;
        if (cell === 2) gm.map[ny][nx] = 0;
        gm.px = nx; gm.py = ny;
        if (gm.map[ny][nx] === 3) { gm.map[ny][nx] = 0; gm.got++; gm.score += 20; }
        if (gm.map[ny][nx] === 4 && gm.got >= 3) return "win";
      },
      paint(gm) {
        g.fillStyle = "#1A120C"; g.fillRect(0, HUD, W, H - HUD);
        for (let y = 0; y < 12; y++) for (let x = 0; x < 10; x++) {
          const c = gm.map[y][x];
          if (c === 1) { g.fillStyle = "#5A4030"; g.fillRect(x * 24, 24 + y * 22, 23, 21); }
          else if (c === 2) { g.fillStyle = "#3A2A22"; g.fillRect(x * 24 + 4, 28 + y * 22, 16, 14); }
          else if (c === 3) { g.fillStyle = CYAN; g.fillRect(x * 24 + 8, 30 + y * 22, 8, 8); }
          else if (c === 4) { g.fillStyle = LIME; g.fillRect(x * 24 + 4, 28 + y * 22, 16, 16); }
        }
        g.fillStyle = GOLD; g.fillRect(gm.px * 24 + 6, 28 + gm.py * 22, 12, 14);
        text(gm.got + "/3", 8, 292, CREAM);
      }
    },
    16: {
      init(gm) { gm.x = 120; gm.y = 60; gm.vx = 0; gm.vy = 0; gm.pad = 90 + Math.random() * 60; },
      step(gm, dt, p) {
        gm.vy += 28 * dt;
        if (p.down) { gm.vy -= 55 * dt; gm.vx += clamp(p.x - gm.x, -1, 1) * 40 * dt; gm.score += dt; }
        gm.x += gm.vx * dt; gm.y += gm.vy * dt;
        gm.x = clamp(gm.x, 16, 224);
        if (gm.y > 286) {
          if (Math.abs(gm.x - gm.pad) < 28 && Math.abs(gm.vy) < 28) { gm.score += 100; return "win"; }
          return "dead";
        }
      },
      paint(gm) {
        g.fillStyle = "#0C1024"; g.fillRect(0, HUD, W, H - HUD);
        g.fillStyle = "#6A6A78"; g.fillRect(0, 300, W, 20);
        g.fillStyle = LIME; g.fillRect(gm.pad - 24, 296, 48, 6);
        g.fillStyle = CREAM; g.fillRect(gm.x - 8, gm.y, 16, 14);
        if (P.down) { g.fillStyle = ORANGE; g.fillRect(gm.x - 3, gm.y + 14, 6, 6); }
      }
    },
    17: {
      init(gm) { gm.x = 120; gm.y = 200; gm.vy = -80; gm.bars = []; for (let i = 0; i < 6; i++) gm.bars.push({x: 30 + Math.random() * 140, y: 40 + i * 46}); },
      step(gm, dt, p) {
        if (p.down) gm.x += clamp(p.x - gm.x, -140 * dt, 140 * dt);
        gm.vy += 80 * dt; gm.y += gm.vy * dt;
        gm.bars.forEach(b => {
          if (gm.vy > 0 && gm.y > b.y - 4 && gm.y < b.y + 8 && Math.abs(gm.x - b.x) < 28) { gm.vy = -150; gm.score += 10; b.y += 280; b.x = 30 + Math.random() * 150; }
        });
        gm.bars.forEach(b => { if (b.y > 320) b.y = 30; });
        if (gm.y > 318 || gm.y < 20) return "dead";
      },
      paint(gm) {
        g.fillStyle = "#101828"; g.fillRect(0, HUD, W, H - HUD);
        g.fillStyle = GOLD; gm.bars.forEach(b => g.fillRect(b.x - 24, b.y, 48, 6));
        g.fillStyle = CYAN; g.fillRect(gm.x - 6, gm.y - 10, 12, 12);
      }
    },
    18: {
      init(gm) { gm.x = 120; gm.guys = []; gm.t = 0; },
      step(gm, dt, p) {
        gm.t += dt;
        if (p.down) gm.x = clamp(p.x, 24, 216);
        if (Math.random() < dt * 0.8) gm.guys.push({x: 40 + Math.random() * 160, y: 30, vy: 40, b: 0});
        gm.guys.forEach(gu => {
          gu.y += gu.vy * dt; gu.vy += 20 * dt;
          if (gu.b < 3 && gu.vy > 0 && gu.y > 270 && Math.abs(gu.x - gm.x) < 28) { gu.vy = -90; gu.b++; gm.score += 10; }
          if (gu.b >= 3 && gu.y < 40) { gu.saved = 1; gm.score += 30; }
        });
        if (gm.guys.some(gu => gu.y > 316)) return "dead";
        gm.guys = gm.guys.filter(gu => !gu.saved && gu.y < 330);
      },
      paint(gm) {
        g.fillStyle = "#1A2430"; g.fillRect(0, HUD, W, H - HUD);
        g.fillStyle = "#C8C8D0"; g.fillRect(gm.x - 22, 286, 44, 6);
        g.fillStyle = RED; g.fillRect(8, 250, 20, 28);
        gm.guys.forEach(gu => { g.fillStyle = GOLD; g.fillRect(gu.x - 4, gu.y, 8, 10); });
      }
    },
    19: {
      init(gm) { gm.z = []; gm.ammo = 6; gm.t = 0; },
      step(gm, dt, p) {
        gm.t += dt;
        if (Math.random() < dt * 0.8) gm.z.push({x: 30 + Math.random() * 180, y: 40, head: true});
        gm.z.forEach(z => z.y += 22 * dt);
        if (p.tap && p.y > 30 && p.y < 250) {
          if (gm.ammo <= 0) return;
          gm.ammo--;
          const z = gm.z.find(z => Math.abs(p.x - z.x) < 16 && Math.abs(p.y - z.y) < 20);
          if (z) { z.dead = 1; gm.score += Math.abs(p.y - z.y) < 8 ? 25 : 10; }
        }
        if (Math.random() < dt * 0.15) gm.ammo = Math.min(6, gm.ammo + 1);
        if (gm.z.some(z => z.y > 280)) return "dead";
        gm.z = gm.z.filter(z => !z.dead && z.y < 300);
      },
      paint(gm) {
        g.fillStyle = "#10140C"; g.fillRect(0, HUD, W, H - HUD);
        gm.z.forEach(z => { g.fillStyle = "#3C6A32"; g.fillRect(z.x - 8, z.y, 16, 22); g.fillStyle = "#C8D0A0"; g.fillRect(z.x - 6, z.y - 8, 12, 8); });
        text("BALLES " + gm.ammo, 8, 292, GOLD);
      }
    },
    20: {
      init(gm) {
        gm.maze = [
          "##########",
          "#S..#....#",
          "#.##.##..#",
          "#.#*...#.#",
          "#.#.##.#.#",
          "#...#*...#",
          "###.#.##.#",
          "#*..#....#",
          "#.#####.##",
          "#........E",
          "##########"
        ];
        gm.x = 1; gm.y = 1; gm.left = 3; gm.acc = 0; gm.time = 40;
      },
      step(gm, dt, p) {
        gm.time -= dt;
        if (gm.time <= 0) return "lose";
        gm.acc += dt;
        if (!p.down || gm.acc < 0.12) return;
        gm.acc = 0;
        const tx = clamp(p.x / 24 | 0, 0, 9), ty = clamp((p.y - 28) / 24 | 0, 0, 10);
        const dx = Math.sign(tx - gm.x), dy = Math.abs(tx - gm.x) >= Math.abs(ty - gm.y) ? 0 : Math.sign(ty - gm.y);
        const nx = gm.x + (dy ? 0 : dx), ny = gm.y + dy;
        const c = gm.maze[ny][nx];
        if (c === "#") return;
        gm.x = nx; gm.y = ny;
        if (c === "*") { gm.maze[ny] = gm.maze[ny].slice(0, nx) + "." + gm.maze[ny].slice(nx + 1); gm.left--; gm.score += 15; }
        if (c === "E" && gm.left <= 0) return "win";
      },
      paint(gm) {
        g.fillStyle = NIGHT; g.fillRect(0, HUD, W, H - HUD);
        gm.maze.forEach((row, y) => { for (let x = 0; x < row.length; x++) {
          const c = row[x];
          if (c === "#") { g.fillStyle = TEAL; g.fillRect(x * 24, 28 + y * 24, 23, 23); }
          else if (c === "*") { g.fillStyle = GOLD; g.fillRect(x * 24 + 8, 36 + y * 24, 8, 8); }
          else if (c === "E") { g.fillStyle = LIME; g.fillRect(x * 24 + 4, 32 + y * 24, 16, 16); }
        }});
        g.fillStyle = CREAM; g.beginPath(); g.arc(gm.x * 24 + 12, 40 + gm.y * 24, 6, 0, 7); g.fill();
        text(Math.max(0, gm.time | 0) + "s", 8, 300, GOLD);
      }
    },
    22: {
      init(gm) { gm.lit = 0; gm.trap = false; gm.wait = 1.2; gm.need = 0.9; },
      step(gm, dt, p) {
        gm.wait -= dt;
        if (gm.wait <= 0) { gm.lit = Math.random() * 4 | 0; gm.trap = Math.random() < 0.18; gm.wait = gm.need; gm.need = Math.max(0.35, gm.need - 0.03); }
        if (!p.tap || p.y < 40) return;
        const i = (p.x > 120 ? 1 : 0) + (p.y > 170 ? 2 : 0);
        if (i === gm.lit) { if (gm.trap) return "dead"; gm.score += 10; gm.lit = -1; }
        else return "dead";
      },
      paint(gm) {
        g.fillStyle = NIGHT; g.fillRect(0, HUD, W, H - HUD);
        for (let i = 0; i < 4; i++) {
          const x = 16 + (i % 2) * 108, y = 48 + (i / 2 | 0) * 110;
          g.fillStyle = i === gm.lit ? (gm.trap ? WHITE : GOLD) : PANEL;
          g.fillRect(x, y, 100, 100);
        }
      }
    },
    23: {
      init(gm) {
        gm.sw = [0, 0, 0];
        gm.trains = [{color: RED, y: 40, lane: 0, need: 0}];
        gm.t = 0; gm.sent = 0;
      },
      step(gm, dt, p) {
        gm.t += dt;
        if (p.tap) {
          const i = [70, 140, 210].findIndex(yy => Math.abs(p.y - yy) < 18);
          if (i >= 0) gm.sw[i] = 1 - gm.sw[i];
        }
        if (gm.trains.length < 3 && Math.random() < dt * 0.5) {
          const need = Math.random() * 2 | 0;
          gm.trains.push({color: need ? CYAN : RED, y: 30, lane: 0, need});
        }
        gm.trains.forEach(t => {
          t.y += 36 * dt;
          [70, 140, 210].forEach((yy, i) => { if (!t.done && Math.abs(t.y - yy) < 4) t.lane = gm.sw[i]; });
          if (t.y > 280) { t.done = 1; if (t.lane === t.need) { gm.score += 20; gm.sent++; } else t.bad = 1; }
        });
        if (gm.trains.some(t => t.bad)) return "dead";
        gm.trains = gm.trains.filter(t => !t.done);
        if (gm.sent >= 8) return "win";
      },
      paint(gm) {
        g.fillStyle = "#1A140C"; g.fillRect(0, HUD, W, H - HUD);
        g.strokeStyle = GREY; g.strokeRect(40.5, 30.5, 70, 250); g.strokeRect(130.5, 30.5, 70, 250);
        text("ROUGE", 48, 36, RED); text("BLEU", 142, 36, CYAN);
        [70, 140, 210].forEach((yy, i) => { g.fillStyle = gm.sw[i] ? CYAN : RED; g.fillRect(100, yy - 6, 40, 12); });
        gm.trains.forEach(t => { g.fillStyle = t.color; g.fillRect(t.lane ? 150 : 56, t.y, 28, 12); });
      }
    },
    25: {
      init(gm) { gm.ev = 0; gm.x = 20; gm.phase2 = "run"; gm.alt = 0; gm.last = ""; gm.jump = 0; gm.birds = []; gm.t = 0; },
      step(gm, dt, p) {
        if (gm.cleared) return "win";
        gm.t += dt;
        const left = p.tap && p.x < 120 && p.y > 250;
        const right = p.tap && p.x >= 120 && p.y > 250;
        const jump = p.tap && p.y > 220 && p.y < 250;
        if (gm.ev === 2) {
          if (Math.random() < dt) gm.birds.push({x: 240, y: 60 + Math.random() * 80});
          gm.birds.forEach(b => b.x -= 90 * dt);
          if (p.tap && p.y < 200) {
            const b = gm.birds.find(b => Math.abs(p.x - b.x) < 14 && Math.abs(p.y - b.y) < 12);
            if (b) { b.dead = 1; gm.score += 15; }
          }
          gm.birds = gm.birds.filter(b => !b.dead && b.x > 0);
          if (gm.t > 12) { nextEv(gm); }
          return;
        }
        if (left && gm.last !== "L") { gm.x += 8; gm.last = "L"; gm.alt++; }
        if (right && gm.last !== "R") { gm.x += 8; gm.last = "R"; gm.alt++; }
        if (jump) gm.jump = 0.45;
        if (gm.jump > 0) gm.jump -= dt;
        if (gm.ev === 0 && gm.x > 200) { gm.score += 40; nextEv(gm); }
        if (gm.ev === 1 && gm.x > 180) { if (gm.jump > 0) { gm.score += 40; nextEv(gm); } else return "dead"; }
        if (gm.ev === 3 && gm.x > 200) { gm.score += 40; nextEv(gm); }
        if (gm.ev === 3 && [70, 120, 170].some(h => Math.abs(gm.x - h) < 6 && gm.jump <= 0)) return "dead";
      },
      paint(gm) {
        g.fillStyle = "#87C8F0"; g.fillRect(0, HUD, W, H - HUD);
        g.fillStyle = "#C47A45"; g.fillRect(0, 180, W, 70);
        text(["COURSE","SAUT","TIR","HAIES"][gm.ev] || "", 8, 28, NIGHT);
        if (gm.ev === 2) gm.birds.forEach(b => { g.fillStyle = WHITE; g.fillRect(b.x, b.y, 12, 6); });
        if (gm.ev === 3) { g.fillStyle = GOLD; [70, 120, 170].forEach(h => g.fillRect(h, 160, 8, 20)); }
        if (gm.ev === 1) { g.fillStyle = WHITE; g.fillRect(176, 168, 8, 40); }
        g.fillStyle = RED; g.fillRect(gm.x, gm.jump > 0 ? 150 : 164, 12, 16);
        button(8, 260, 100, 44, "GAUCHE", TEAL, CREAM);
        button(132, 260, 100, 44, "DROITE", REDP, CREAM);
        if (gm.ev === 1 || gm.ev === 3) button(70, 220, 100, 28, "SAUT", YELLOW, BLACK);
      }
    }
  };

  function shooter(boss) {
    return {
      init(gm) { gm.x = 120; gm.bullets = []; gm.foes = []; gm.cd = 0; gm.boss = boss ? 1 : 0; gm.hp = boss ? 12 : 0; },
      step(gm, dt, p) {
        if (p.down) gm.x = clamp(p.x, 16, 224);
        gm.cd -= dt;
        if (gm.cd <= 0) { gm.bullets.push({x: gm.x, y: 286}); gm.cd = 0.22; }
        gm.bullets.forEach(b => b.y -= 260 * dt);
        gm.bullets = gm.bullets.filter(b => b.y > 20);
        if (!boss && Math.random() < dt * 1.5) gm.foes.push({x: 20 + Math.random() * 200, y: 30, vy: 28 + Math.random() * 20});
        if (boss && !gm.foes.length) gm.foes.push({x: 120, y: 70, vy: 10, boss: 1});
        gm.foes.forEach(f => { f.y += f.vy * dt; if (f.boss) f.x = 120 + Math.sin(performance.now() / 400) * 70; });
        gm.bullets.forEach(b => gm.foes.forEach(f => {
          if (!f.dead && Math.abs(b.x - f.x) < (f.boss ? 22 : 12) && Math.abs(b.y - f.y) < (f.boss ? 16 : 10)) {
            b.dead = 1;
            if (f.boss) { gm.hp--; gm.score += 5; if (gm.hp <= 0) { f.dead = 1; gm.boss++; if (gm.boss > 4) gm.win = 1; else { gm.hp = 10 + gm.boss * 4; f.dead = 0; } } }
            else { f.dead = 1; gm.score += 15; }
          }
        }));
        if (gm.win) return "win";
        if (gm.foes.some(f => !f.dead && f.y > 280 && Math.abs(f.x - gm.x) < 16)) return "dead";
        gm.foes = gm.foes.filter(f => !f.dead && f.y < 330);
        gm.bullets = gm.bullets.filter(b => !b.dead);
      },
      paint(gm) {
        g.fillStyle = "#070712"; g.fillRect(0, HUD, W, H - HUD);
        gm.foes.forEach(f => { g.fillStyle = f.boss ? REDP : PINK; g.fillRect(f.x - (f.boss ? 18 : 8), f.y - 6, f.boss ? 36 : 16, f.boss ? 16 : 10); });
        g.fillStyle = GOLD; gm.bullets.forEach(b => g.fillRect(b.x - 1, b.y, 2, 6));
        g.fillStyle = CYAN; g.fillRect(gm.x - 10, 292, 20, 10);
        if (boss) text("BOSS " + gm.boss, 8, 26, GOLD);
      }
    };
  }
  function faller(crystal) {
    return {
      init(gm) { gm.x = 120; gm.items = []; },
      step(gm, dt, p) {
        if (p.down) gm.x = clamp(p.x, 20, 220);
        if (Math.random() < dt * 2) gm.items.push({x: 16 + Math.random() * 200, y: 24, bad: Math.random() < (crystal ? .35 : .55), vy: 60 + Math.random() * 40});
        gm.items.forEach(it => it.y += it.vy * dt);
        gm.items.forEach(it => {
          if (it.y > 286 && Math.abs(it.x - gm.x) < 18) { it.got = 1; if (it.bad) it.boom = 1; else gm.score += crystal ? 15 : 10; }
        });
        if (gm.items.some(it => it.boom)) return "dead";
        gm.items = gm.items.filter(it => !it.got && it.y < 320);
      },
      paint(gm) {
        g.fillStyle = crystal ? "#140C28" : "#101820"; g.fillRect(0, HUD, W, H - HUD);
        gm.items.forEach(it => { g.fillStyle = it.bad ? RED : (crystal ? CYAN : GOLD); g.fillRect(it.x - 5, it.y, 10, 10); });
        g.fillStyle = crystal ? "#C8A0FF" : CREAM; g.fillRect(gm.x - 16, 292, 32, 10);
      }
    };
  }
  const PIECES = [
    [[[0,0],[1,0],[2,0],[3,0]],[[1,-1],[1,0],[1,1],[1,2]]],
    [[[0,0],[1,0],[0,1],[1,1]]],
    [[[1,0],[0,1],[1,1],[2,1]],[[0,0],[0,1],[1,1],[0,2]]],
    [[[0,0],[1,0],[2,0],[2,1]],[[1,0],[1,1],[1,2],[0,2]]]
  ];
  function randPiece() { return Math.random() * PIECES.length | 0; }
  function pieceCells(id, rot) { const p = PIECES[id]; return p[rot % p.length]; }
  function fit(gm, x, y, rot) {
    return pieceCells(gm.piece, rot).every(c => {
      const nx = x + c[0], ny = y + c[1];
      return nx >= 0 && nx < 8 && ny >= 0 && ny < 16 && !gm.grid[ny][nx];
    });
  }
  function lockPiece(gm) {
    pieceCells(gm.piece, gm.rot).forEach(c => { const ny = gm.y + c[1], nx = gm.x + c[0]; if (gm.grid[ny]) gm.grid[ny][nx] = gm.piece + 1; });
  }
  function clearLines(gm) {
    let n = 0;
    gm.grid = gm.grid.filter(row => { if (row.every(Boolean)) { n++; return false; } return true; });
    while (gm.grid.length < 16) gm.grid.unshift(Array(8).fill(0));
    return n;
  }
  function cardAt(x, y) {
    if (y < 48) return -1;
    const c = (x - 12) / 56 | 0, r = (y - 48) / 64 | 0;
    if (c < 0 || c > 3 || r < 0 || r > 3) return -1;
    return r * 4 + c;
  }
  function nextEv(gm) {
    gm.ev++;
    gm.x = 20; gm.jump = 0; gm.t = 0; gm.birds = [];
    if (gm.ev >= 4) gm.cleared = 1;
  }

  function drawPlay() {
    if (!game) return;
    if (game.phase === "title") drawTitle(game);
    else { game.paint(); hud(game); if (game.phase === "over") drawOver(game); }
  }
  function draw() {
    if (mode === "cal") drawCal();
    else if (mode === "meteo") drawMeteo();
    else if (mode === "set") drawSet();
    else if (mode === "note") drawNote();
    else if (mode === "jeu") drawJeu();
    else if (mode === "gift") drawGift();
    else if (mode === "locked") drawLocked();
    else if (mode === "saver") drawSaver();
    else if (mode === "wifi") drawWifi();
    else if (mode === "ptr") drawPtr();
    else if (mode === "clock") drawClock();
    else if (mode === "city") drawCity();
    else if (mode === "play") drawPlay();
  }

  function pointer(e) {
    const r = cv.getBoundingClientRect();
    P.x = (e.clientX - r.left) / r.width * W;
    P.y = (e.clientY - r.top) / r.height * H;
  }
  let last = performance.now(), holdArm = 0;
  function frame(t) {
    const dt = Math.min(0.05, (t - last) / 1000); last = t;
    st.blink += dt * 2;
    const p = parts();
    if (!st.fake) st.fakeClock = p;
    else { st.fake.ss = (st.fake.ss || 0) + dt; if (st.fake.ss >= 60) { st.fake.ss -= 60; st.fake.mm++; if (st.fake.mm >= 60) { st.fake.mm = 0; st.fake.hh = (st.fake.hh + 1) % 24; } } }
    if (keys.ArrowLeft) P.x = 24;
    if (keys.ArrowRight) P.x = 216;
    if (keys.ArrowUp) P.y = 40;
    if (keys.ArrowDown) P.y = 290;
    const tap = P.tap; P.tap = false;
    try {
      if (mode === "play" && game) runGame(dt, {x: P.x, y: P.y, down: P.down || keys.ArrowLeft || keys.ArrowRight, tap});
      else if (tap) tapUI(P.x, P.y);
    } catch (err) { console.error(err); mode = "cal"; game = null; }
    if (mode === "jeu" && P.down && P.y < 42) {
      if (!holdArm) holdArm = t;
      if (t - holdArm > 2000 && !P.held) {
        st.test = !st.test; st.rec.test = st.test; saveRec(); P.held = true;
        if (opt.onClock) opt.onClock();
      }
    } else holdArm = 0;
    if ((mode === "cal" || mode === "meteo") && t - st.idle > 45000) {
      st.saverFrom = mode; mode = "saver"; st.saverNext = t; if (!st.sheet) { st.sheet = new Image(); st.sheet.src = "firmware/veille.png"; }
    }
    if (mode === "saver" && t > st.saverNext + 30000) { st.saverImg = (st.saverImg + 1) % 12; st.saverNext = t; }
    if (mode === "gift" || mode === "play") st.blink += 0;
    try { draw(); } catch (err) { console.error(err); }
    requestAnimationFrame(frame);
  }

  function bootAdvent() {
    const p = parts();
    if (p.m === 12 && p.d <= 25 && st.seen !== keyOf(p.y, p.m, p.d)) {
      st.seen = keyOf(p.y, p.m, p.d);
      st.rec.seen = st.seen; saveRec();
      st.vm = 12; st.vy = p.y;
      openGift(p.d);
    }
  }

  window.Screen = {
    start(options) {
      opt = options || {};
      cv = document.querySelector("#scr");
      g = cv.getContext("2d");
      g.imageSmoothingEnabled = false;
      const p = parts();
      st.vy = p.y; st.vm = p.m; st.sel = [p.y, p.m, p.d];
      st.notes = store.load("cg-notes", null) || defaultNotes();
      st.rec = store.load("cg-rec", {});
      st.test = !!st.rec.test; st.muet = !!st.rec.muet; st.seen = st.rec.seen || "";
      st.idle = performance.now();
      cv.addEventListener("pointerdown", e => { pointer(e); P.down = true; P.tap = true; P.held = false; st.idle = performance.now(); P.t0 = performance.now(); cv.setPointerCapture(e.pointerId); });
      cv.addEventListener("pointermove", pointer);
      cv.addEventListener("pointerup", () => {
        if (mode === "jeu" && P.y < 42 && P.x < 60 && !P.held && performance.now() - P.t0 < 2000) {
          st.muet = !st.muet; st.rec.muet = st.muet; saveRec();
        }
        P.down = false;
      });
      cv.addEventListener("pointercancel", () => { P.down = false; });
      cv.addEventListener("keydown", e => {
        if (e.key in {ArrowLeft:1, ArrowRight:1, ArrowUp:1, ArrowDown:1}) { keys[e.key] = true; e.preventDefault(); }
        if (e.key === "Enter" || e.key === " ") { P.tap = true; e.preventDefault(); }
        if (e.key === "Escape") { if (mode === "play") { mode = "jeu"; game = null; ping(); } }
      });
      cv.addEventListener("keyup", e => { keys[e.key] = false; });
      bootAdvent();
      ping();
      requestAnimationFrame(frame);
      return Screen;
    },
    go(next) { if (next === "agenda") next = "cal"; if (next === "advent") next = "jeu"; if (next === "regl") next = "set"; go(next); },
    openCart(day) {
      st.day = day;
      if (unlocked(day)) bootGame(day);
      else { mode = "locked"; ping(); }
    },
    setCity(i) { st.city = i; if (mode === "meteo" || mode === "cal") st.msg = "VILLE " + cityName(); },
    unlocked,
    test() { return st.test; }
  };
})();
