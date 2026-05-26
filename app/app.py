import os
import psycopg2
import psycopg2.extras
import requests as req_lib
import secrets
import pathlib
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from datetime import datetime, date, timedelta
import time

app = Flask(__name__)

# ─── SECRET KEY (auto-generata e persistita su volume) ────────────────────────
_key_file = pathlib.Path("/data/secret.key")
if not _key_file.exists():
    _key_file.parent.mkdir(parents=True, exist_ok=True)
    _key_file.write_text(secrets.token_hex(32))
app.secret_key = _key_file.read_text().strip()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://repuser:reppass@postgres:5432/reperibilita')

# ─── TRADUZIONI ───────────────────────────────────────────────────────────────
TRANSLATIONS = {
    'it': {
        'app_name': 'OnCall Tracker',
        'nav_home': 'Home', 'nav_settings': 'Impostazioni',
        'stat_calls_month': 'Chiamate questo mese', 'stat_duration': 'Durata totale',
        'stat_call_cost': 'Costo chiamate', 'stat_total': 'Totale mese',
        'new_call': 'Nuova Chiamata', 'new_oncall': 'Nuovo Periodo Reperibilità',
        'datetime': 'Data e Ora', 'duration_min': 'Durata (minuti)',
        'workorder': 'Commessa / Impianto', 'description': 'Descrizione / Note',
        'add_call': '＋ Aggiungi Chiamata', 'add_oncall': '＋ Aggiungi Reperibilità',
        'date_start': 'Data Inizio', 'date_end': 'Data Fine', 'notes': 'Note',
        'history': 'Storico', 'last_records': 'Ultimi 50 record',
        'tab_calls': 'Chiamate', 'tab_oncall': 'Reperibilità',
        'col_datetime': 'Data/Ora', 'col_duration': 'Durata', 'col_workorder': 'Commessa',
        'col_description': 'Descrizione', 'col_cost': 'Costo',
        'col_from': 'Dal', 'col_to': 'Al', 'col_days': 'Giorni', 'col_notes': 'Note',
        'no_calls': 'Nessuna chiamata registrata.', 'no_oncall': 'Nessun periodo registrato.',
        'formula_call': 'Costo = (durata/60 × €{}/h) + €{}/chiamata',
        'formula_oncall': 'Costo = giorni × €{}/giorno',
        'settings_title': 'Impostazioni Costi',
        'hourly_rate': 'Costo Orario (€/ora)', 'hourly_rate_hint': 'Applicato proporzionalmente alla durata della chiamata.',
        'per_call_rate': 'Costo per Chiamata (€)', 'per_call_hint': 'Aggiunto fisso ad ogni chiamata.',
        'per_day_rate': 'Costo Reperibilità (€/giorno)', 'per_day_hint': 'Moltiplicato per il numero di giorni.',
        'formula_title': 'Formula di calcolo:', 'formula_call_label': 'Chiamata', 'formula_oncall_label': 'Reperibilità',
        'save_settings': '✔ Salva Impostazioni', 'settings_saved': 'Impostazioni salvate.',
        'last_update': 'Ultimo aggiornamento', 'settings_note': 'Le modifiche ai costi non ricalcolano i record esistenti.',
        'weekend_section': 'Tariffe Weekend', 'weekend_call_toggle': 'Tariffa diversa per chiamate nel weekend',
        'weekend_oncall_toggle': 'Tariffa diversa per reperibilità nel weekend',
        'hourly_rate_we': 'Costo Orario Weekend (€/ora)', 'per_call_rate_we': 'Costo per Chiamata Weekend (€)',
        'per_day_rate_we': 'Costo Reperibilità Weekend (€/giorno)',
        'weekend_hint': 'Se non abilitato, viene usata la tariffa standard anche nel weekend.',
        'grafana_section': 'Collegamento Grafana', 'grafana_url_lbl': 'URL Grafana',
        'grafana_url_hint': 'Es. http://100.x.x.x:3000 se accedi via Tailscale',
        'tg_title': 'Notifiche Telegram', 'tg_enabled': 'Abilita notifiche Telegram',
        'tg_token': 'Bot Token', 'tg_chat_id': 'Chat ID',
        'tg_notify_start': 'Notifica inizio reperibilità', 'tg_notify_end': 'Notifica fine reperibilità',
        'tg_test': '📨 Invia messaggio di test', 'tg_save': '💾 Salva configurazione Telegram',
        'tg_saved': 'Configurazione Telegram salvata.',
        'tg_test_sent': 'Messaggio di test inviato!', 'tg_test_fail': 'Invio fallito: {}',
        'tg_msg_start': '🟢 <b>Inizio reperibilità</b>\n📅 Dal <b>{}</b> al <b>{}</b>\n📝 {}',
        'tg_msg_end':   '🔴 <b>Fine reperibilità</b>\n📅 Dal <b>{}</b> al <b>{}</b>\n📝 {}',
        'tg_msg_test': '✅ <b>OnCall Tracker</b> — test connessione riuscito!',
        'tg_how_title': 'Come configurare il bot',
        'tg_how_1': 'Cerca <b>@BotFather</b> su Telegram', 'tg_how_2': 'Invia <code>/newbot</code> e segui le istruzioni per ottenere il <b>Token</b>',
        'tg_how_3': 'Invia un messaggio al bot, poi visita <code>https://api.telegram.org/bot&lt;TOKEN&gt;/getUpdates</code> per il <b>Chat ID</b>',
        'tg_how_4': 'Incolla Token e Chat ID qui sotto, abilita e salva',
        'btn_notify_end': '🔔 Fine', 'notify_end_sent': 'Notifica fine reperibilità inviata.',
        'call_added': 'Chiamata aggiunta — Costo: €{}', 'call_updated': 'Chiamata aggiornata.',
        'call_deleted': 'Chiamata eliminata.', 'oncall_added': 'Reperibilità aggiunta — Costo: €{}',
        'oncall_deleted': 'Periodo eliminato.', 'edit_call': 'Modifica Chiamata',
        'save': 'Salva', 'cancel': 'Annulla',
        'confirm_delete_call': 'Eliminare questa chiamata?', 'confirm_delete_oncall': 'Eliminare questo periodo?',
        'sat': 'Sab', 'sun': 'Dom',
    },
    'en': {
        'app_name': 'OnCall Tracker',
        'nav_home': 'Home', 'nav_settings': 'Settings',
        'stat_calls_month': 'Calls this month', 'stat_duration': 'Total duration',
        'stat_call_cost': 'Call cost', 'stat_total': 'Month total',
        'new_call': 'New Call', 'new_oncall': 'New On-Call Period',
        'datetime': 'Date & Time', 'duration_min': 'Duration (minutes)',
        'workorder': 'Work Order / Plant', 'description': 'Description / Notes',
        'add_call': '＋ Add Call', 'add_oncall': '＋ Add On-Call Period',
        'date_start': 'Start Date', 'date_end': 'End Date', 'notes': 'Notes',
        'history': 'History', 'last_records': 'Last 50 records',
        'tab_calls': 'Calls', 'tab_oncall': 'On-Call',
        'col_datetime': 'Date/Time', 'col_duration': 'Duration', 'col_workorder': 'Work Order',
        'col_description': 'Description', 'col_cost': 'Cost',
        'col_from': 'From', 'col_to': 'To', 'col_days': 'Days', 'col_notes': 'Notes',
        'no_calls': 'No calls recorded yet.', 'no_oncall': 'No on-call periods recorded yet.',
        'formula_call': 'Cost = (duration/60 × €{}/h) + €{}/call',
        'formula_oncall': 'Cost = days × €{}/day',
        'settings_title': 'Cost Settings',
        'hourly_rate': 'Hourly Rate (€/hr)', 'hourly_rate_hint': 'Applied proportionally to the call duration.',
        'per_call_rate': 'Per-Call Fee (€)', 'per_call_hint': 'Fixed amount added to every call.',
        'per_day_rate': 'On-Call Rate (€/day)', 'per_day_hint': 'Multiplied by the number of days.',
        'formula_title': 'Calculation formula:', 'formula_call_label': 'Call', 'formula_oncall_label': 'On-Call',
        'save_settings': '✔ Save Settings', 'settings_saved': 'Settings saved.',
        'last_update': 'Last update', 'settings_note': 'Changing rates does not recalculate existing records.',
        'weekend_section': 'Weekend Rates', 'weekend_call_toggle': 'Different rate for calls on weekends',
        'weekend_oncall_toggle': 'Different rate for on-call on weekends',
        'hourly_rate_we': 'Weekend Hourly Rate (€/hr)', 'per_call_rate_we': 'Weekend Per-Call Fee (€)',
        'per_day_rate_we': 'Weekend On-Call Rate (€/day)',
        'weekend_hint': 'If disabled, the standard rate is used on weekends too.',
        'grafana_section': 'Grafana Link', 'grafana_url_lbl': 'Grafana URL',
        'grafana_url_hint': 'E.g. http://100.x.x.x:3000 if accessing via Tailscale',
        'tg_title': 'Telegram Notifications', 'tg_enabled': 'Enable Telegram notifications',
        'tg_token': 'Bot Token', 'tg_chat_id': 'Chat ID',
        'tg_notify_start': 'Notify on-call start', 'tg_notify_end': 'Notify on-call end',
        'tg_test': '📨 Send test message', 'tg_save': '💾 Save Telegram config',
        'tg_saved': 'Telegram configuration saved.',
        'tg_test_sent': 'Test message sent!', 'tg_test_fail': 'Send failed: {}',
        'tg_msg_start': '🟢 <b>On-call started</b>\n📅 From <b>{}</b> to <b>{}</b>\n📝 {}',
        'tg_msg_end':   '🔴 <b>On-call ended</b>\n📅 From <b>{}</b> to <b>{}</b>\n📝 {}',
        'tg_msg_test': '✅ <b>OnCall Tracker</b> — connection test successful!',
        'tg_how_title': 'How to set up the bot',
        'tg_how_1': 'Search <b>@BotFather</b> on Telegram', 'tg_how_2': 'Send <code>/newbot</code> and follow the steps to get your <b>Token</b>',
        'tg_how_3': 'Send a message to your bot, then visit <code>https://api.telegram.org/bot&lt;TOKEN&gt;/getUpdates</code> to get the <b>Chat ID</b>',
        'tg_how_4': 'Paste Token and Chat ID below, enable and save',
        'btn_notify_end': '🔔 End', 'notify_end_sent': 'On-call end notification sent.',
        'call_added': 'Call added — Cost: €{}', 'call_updated': 'Call updated.',
        'call_deleted': 'Call deleted.', 'oncall_added': 'On-call period added — Cost: €{}',
        'oncall_deleted': 'Period deleted.', 'edit_call': 'Edit Call',
        'save': 'Save', 'cancel': 'Cancel',
        'confirm_delete_call': 'Delete this call?', 'confirm_delete_oncall': 'Delete this period?',
        'sat': 'Sat', 'sun': 'Sun',
    }
}

def t(key):
    lang = session.get('lang', 'it')
    return TRANSLATIONS.get(lang, TRANSLATIONS['it']).get(key, key)

def get_lang():
    return session.get('lang', 'it')

@app.context_processor
def inject_globals():
    imp = get_impostazioni()
    grafana_url = imp['grafana_url'] if imp and imp.get('grafana_url') else 'http://localhost:3000/d/reperibilita-main-v1'
    return dict(t=t, lang=get_lang(), grafana_url=grafana_url)

# ─── DB ───────────────────────────────────────────────────────────────────────
def get_db():
    return psycopg2.connect(DATABASE_URL)

def migrate_db():
    """Aggiunge colonne mancanti per upgrade da versioni precedenti."""
    new_columns = [
        ("weekend_call_enabled",        "BOOLEAN DEFAULT FALSE"),
        ("costo_orario_weekend",        "DECIMAL(10,2) DEFAULT 25.00"),
        ("costo_per_chiamata_weekend",  "DECIMAL(10,2) DEFAULT 10.00"),
        ("weekend_oncall_enabled",      "BOOLEAN DEFAULT FALSE"),
        ("costo_reperibilita_weekend",  "DECIMAL(10,2) DEFAULT 50.00"),
        ("grafana_url",                 "VARCHAR(200) DEFAULT 'http://localhost:3000/d/reperibilita-main-v1'"),
    ]
    conn = get_db(); cur = conn.cursor()
    for col, definition in new_columns:
        cur.execute(f"""
            DO $$ BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='impostazioni' AND column_name='{col}'
              ) THEN
                ALTER TABLE impostazioni ADD COLUMN {col} {definition};
              END IF;
            END $$;
        """)
    conn.commit(); cur.close(); conn.close()

def get_impostazioni():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM impostazioni ORDER BY id DESC LIMIT 1")
    row = cur.fetchone(); cur.close(); conn.close()
    return row

def get_telegram_config():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM telegram_config ORDER BY id DESC LIMIT 1")
    row = cur.fetchone(); cur.close(); conn.close()
    return row

# ─── CALCOLO COSTI ────────────────────────────────────────────────────────────
def is_weekend(d):
    """Sabato=5, Domenica=6"""
    if isinstance(d, str):
        d = datetime.fromisoformat(d)
    return d.weekday() >= 5

def calcola_costo_chiamata(durata_minuti, data_ora, imp):
    """Usa tariffa weekend se abilitata e la chiamata cade di sabato/domenica."""
    if imp['weekend_call_enabled'] and is_weekend(data_ora):
        orario = float(imp['costo_orario_weekend'])
        per_call = float(imp['costo_per_chiamata_weekend'])
    else:
        orario = float(imp['costo_orario'])
        per_call = float(imp['costo_per_chiamata'])
    return round((durata_minuti / 60.0) * orario + per_call, 2)

def calcola_costo_reperibilita(d1, d2, imp):
    """
    Calcola il costo del periodo reperibilità.
    Se weekend abilitato: conta separatamente giorni feriali e weekend.
    """
    if isinstance(d1, str): d1 = date.fromisoformat(d1)
    if isinstance(d2, str): d2 = date.fromisoformat(d2)

    if imp['weekend_oncall_enabled']:
        tariffa_std = float(imp['costo_reperibilita_giornaliero'])
        tariffa_we  = float(imp['costo_reperibilita_weekend'])
        costo = 0.0
        giorno = d1
        while giorno <= d2:
            costo += tariffa_we if giorno.weekday() >= 5 else tariffa_std
            giorno += timedelta(days=1)
        return round(costo, 2)
    else:
        giorni = (d2 - d1).days + 1
        return round(giorni * float(imp['costo_reperibilita_giornaliero']), 2)

# ─── TELEGRAM ─────────────────────────────────────────────────────────────────
def send_telegram(message):
    try:
        cfg = get_telegram_config()
        if not cfg or not cfg['abilitato'] or not cfg['bot_token'] or not cfg['chat_id']:
            return False, 'Not configured or disabled'
        url = f"https://api.telegram.org/bot{cfg['bot_token']}/sendMessage"
        resp = req_lib.post(url, json={'chat_id': cfg['chat_id'], 'text': message, 'parse_mode': 'HTML'}, timeout=10)
        data = resp.json()
        return (True, '') if data.get('ok') else (False, data.get('description', 'Unknown error'))
    except Exception as e:
        return False, str(e)

def notify_oncall_start(d1, d2, note):
    cfg = get_telegram_config()
    if cfg and cfg['abilitato'] and cfg['notifica_inizio']:
        lang = session.get('lang', 'it')
        send_telegram(TRANSLATIONS[lang]['tg_msg_start'].format(d1, d2, note or '—'))

# ─── LINGUA ───────────────────────────────────────────────────────────────────
@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ('it', 'en'):
        session['lang'] = lang
        try:
            conn = get_db(); cur = conn.cursor()
            cur.execute("UPDATE impostazioni SET lingua=%s WHERE id=(SELECT id FROM impostazioni ORDER BY id DESC LIMIT 1)", (lang,))
            conn.commit(); cur.close(); conn.close()
        except Exception: pass
    return redirect(request.referrer or url_for('index'))

# ─── HOME ─────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, data_ora, durata_minuti, descrizione, commessa, costo_calcolato FROM chiamate ORDER BY data_ora DESC LIMIT 50")
    chiamate = cur.fetchall()
    cur.execute("SELECT id, data_inizio, data_fine, (data_fine - data_inizio + 1) AS giorni, note, costo_calcolato FROM reperibilita ORDER BY data_inizio DESC LIMIT 20")
    reperibilita = cur.fetchall()
    cur.execute("SELECT COUNT(*) AS num_chiamate, COALESCE(SUM(durata_minuti),0) AS tot_minuti, COALESCE(SUM(costo_calcolato),0) AS tot_costo_chiamate FROM chiamate WHERE DATE_TRUNC('month',data_ora)=DATE_TRUNC('month',NOW())")
    stats_chiamate = cur.fetchone()
    cur.execute("SELECT COALESCE(SUM(costo_calcolato),0) AS tot_costo_rep FROM reperibilita WHERE DATE_TRUNC('month',data_inizio)=DATE_TRUNC('month',NOW())")
    stats_rep = cur.fetchone()
    cur.close(); conn.close()
    imp = get_impostazioni()
    if 'lang' not in session and imp and imp.get('lingua'):
        session['lang'] = imp['lingua']
    return render_template('index.html', chiamate=chiamate, reperibilita=reperibilita,
                           stats_chiamate=stats_chiamate, stats_rep=stats_rep,
                           impostazioni=imp, now=datetime.now().strftime('%Y-%m-%dT%H:%M'))

# ─── CHIAMATE ─────────────────────────────────────────────────────────────────
@app.route('/chiamata/aggiungi', methods=['POST'])
def aggiungi_chiamata():
    try:
        data_ora = request.form['data_ora']
        durata = int(request.form['durata_minuti'])
        imp = get_impostazioni()
        costo = calcola_costo_chiamata(durata, data_ora, imp)
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO chiamate (data_ora, durata_minuti, descrizione, commessa, costo_calcolato) VALUES (%s,%s,%s,%s,%s)",
            (data_ora, durata, request.form.get('descrizione','').strip() or None,
             request.form.get('commessa','').strip() or None, costo))
        conn.commit(); cur.close(); conn.close()
        flash(t('call_added').format(f'{costo:.2f}'), 'success')
    except Exception as e: flash(f'Error: {e}', 'danger')
    return redirect(url_for('index'))

@app.route('/chiamata/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_chiamata(id):
    if request.method == 'POST':
        try:
            data_ora = request.form['data_ora']
            durata = int(request.form['durata_minuti'])
            imp = get_impostazioni()
            costo = calcola_costo_chiamata(durata, data_ora, imp)
            conn = get_db(); cur = conn.cursor()
            cur.execute("UPDATE chiamate SET data_ora=%s,durata_minuti=%s,descrizione=%s,commessa=%s,costo_calcolato=%s WHERE id=%s",
                (data_ora, durata, request.form.get('descrizione','').strip() or None,
                 request.form.get('commessa','').strip() or None, costo, id))
            conn.commit(); cur.close(); conn.close()
            flash(t('call_updated'), 'success')
        except Exception as e: flash(f'Error: {e}', 'danger')
        return redirect(url_for('index'))
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM chiamate WHERE id=%s", (id,))
    chiamata = cur.fetchone(); cur.close(); conn.close()
    return render_template('modifica_chiamata.html', chiamata=chiamata)

@app.route('/chiamata/elimina/<int:id>', methods=['POST'])
def elimina_chiamata(id):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("DELETE FROM chiamate WHERE id=%s", (id,))
        conn.commit(); cur.close(); conn.close()
        flash(t('call_deleted'), 'info')
    except Exception as e: flash(f'Error: {e}', 'danger')
    return redirect(url_for('index'))

# ─── REPERIBILITÀ ─────────────────────────────────────────────────────────────
@app.route('/reperibilita/aggiungi', methods=['POST'])
def aggiungi_reperibilita():
    try:
        d1, d2 = request.form['data_inizio'], request.form['data_fine']
        note = request.form.get('note','').strip()
        imp = get_impostazioni()
        costo = calcola_costo_reperibilita(d1, d2, imp)
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO reperibilita (data_inizio,data_fine,note,costo_calcolato) VALUES (%s,%s,%s,%s)",
            (d1, d2, note or None, costo))
        conn.commit(); cur.close(); conn.close()
        notify_oncall_start(d1, d2, note)
        flash(t('oncall_added').format(f'{costo:.2f}'), 'success')
    except Exception as e: flash(f'Error: {e}', 'danger')
    return redirect(url_for('index'))

@app.route('/reperibilita/elimina/<int:id>', methods=['POST'])
def elimina_reperibilita(id):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("DELETE FROM reperibilita WHERE id=%s", (id,))
        conn.commit(); cur.close(); conn.close()
        flash(t('oncall_deleted'), 'info')
    except Exception as e: flash(f'Error: {e}', 'danger')
    return redirect(url_for('index'))

@app.route('/reperibilita/notifica_fine/<int:id>', methods=['POST'])
def notifica_fine_reperibilita(id):
    try:
        conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM reperibilita WHERE id=%s", (id,))
        r = cur.fetchone(); cur.close(); conn.close()
        if r:
            lang = session.get('lang', 'it')
            ok, err = send_telegram(TRANSLATIONS[lang]['tg_msg_end'].format(r['data_inizio'], r['data_fine'], r['note'] or '—'))
            flash(t('notify_end_sent') if ok else t('tg_test_fail').format(err), 'success' if ok else 'danger')
    except Exception as e: flash(f'Error: {e}', 'danger')
    return redirect(url_for('index'))

# ─── IMPOSTAZIONI ─────────────────────────────────────────────────────────────
@app.route('/impostazioni', methods=['GET', 'POST'])
def impostazioni():
    if request.method == 'POST':
        action = request.form.get('action', 'costi')
        if action == 'costi':
            try:
                conn = get_db(); cur = conn.cursor()
                cur.execute("""
                    UPDATE impostazioni SET
                        costo_orario=%s, costo_per_chiamata=%s, costo_reperibilita_giornaliero=%s,
                        weekend_call_enabled=%s, costo_orario_weekend=%s, costo_per_chiamata_weekend=%s,
                        weekend_oncall_enabled=%s, costo_reperibilita_weekend=%s,
                        grafana_url=%s, aggiornato_il=NOW()
                    WHERE id=(SELECT id FROM impostazioni ORDER BY id DESC LIMIT 1)
                """, (
                    float(request.form['costo_orario']),
                    float(request.form['costo_per_chiamata']),
                    float(request.form['costo_reperibilita_giornaliero']),
                    'weekend_call_enabled' in request.form,
                    float(request.form['costo_orario_weekend']),
                    float(request.form['costo_per_chiamata_weekend']),
                    'weekend_oncall_enabled' in request.form,
                    float(request.form['costo_reperibilita_weekend']),
                    request.form.get('grafana_url', 'http://localhost:3000/d/reperibilita-main-v1').strip(),
                ))
                conn.commit(); cur.close(); conn.close()
                flash(t('settings_saved'), 'success')
            except Exception as e: flash(f'Error: {e}', 'danger')
        elif action == 'telegram':
            try:
                conn = get_db(); cur = conn.cursor()
                cur.execute("UPDATE telegram_config SET bot_token=%s,chat_id=%s,notifica_inizio=%s,notifica_fine=%s,abilitato=%s,aggiornato_il=NOW() WHERE id=(SELECT id FROM telegram_config ORDER BY id DESC LIMIT 1)",
                    (request.form.get('bot_token','').strip(), request.form.get('chat_id','').strip(),
                     'notifica_inizio' in request.form, 'notifica_fine' in request.form, 'abilitato' in request.form))
                conn.commit(); cur.close(); conn.close()
                flash(t('tg_saved'), 'success')
            except Exception as e: flash(f'Error: {e}', 'danger')
        elif action == 'telegram_test':
            lang = session.get('lang', 'it')
            ok, err = send_telegram(TRANSLATIONS[lang]['tg_msg_test'])
            flash(t('tg_test_sent') if ok else t('tg_test_fail').format(err), 'success' if ok else 'danger')
        return redirect(url_for('impostazioni'))
    return render_template('impostazioni.html', impostazioni=get_impostazioni(), tg=get_telegram_config())

@app.route('/api/stats')
def api_stats():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT TO_CHAR(DATE_TRUNC('month',data_ora),'YYYY-MM') AS mese, COUNT(*) AS num_chiamate, SUM(durata_minuti) AS tot_minuti, ROUND(SUM(costo_calcolato)::numeric,2) AS tot_costo FROM chiamate GROUP BY DATE_TRUNC('month',data_ora) ORDER BY mese DESC LIMIT 24")
    risultati = cur.fetchall(); cur.close(); conn.close()
    return jsonify({'chiamate_mensili': [dict(r) for r in risultati]})

if __name__ == '__main__':
    for _ in range(30):
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name='impostazioni'")
            ready = cur.fetchone() is not None
            cur.close(); conn.close()
            if ready:
                break
        except Exception:
            pass
        print("Attendo PostgreSQL..."); time.sleep(2)
    migrate_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
