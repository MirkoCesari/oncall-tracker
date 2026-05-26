-- Tabella impostazioni costi
CREATE TABLE IF NOT EXISTS impostazioni (
    id SERIAL PRIMARY KEY,
    costo_orario DECIMAL(10,2) DEFAULT 25.00,
    costo_per_chiamata DECIMAL(10,2) DEFAULT 10.00,
    costo_reperibilita_giornaliero DECIMAL(10,2) DEFAULT 50.00,
    -- Tariffe weekend chiamate
    weekend_call_enabled BOOLEAN DEFAULT FALSE,
    costo_orario_weekend DECIMAL(10,2) DEFAULT 25.00,
    costo_per_chiamata_weekend DECIMAL(10,2) DEFAULT 10.00,
    -- Tariffe weekend reperibilità
    weekend_oncall_enabled BOOLEAN DEFAULT FALSE,
    costo_reperibilita_weekend DECIMAL(10,2) DEFAULT 50.00,
    -- UI
    lingua VARCHAR(5) DEFAULT 'it',
    grafana_url VARCHAR(200) DEFAULT 'http://localhost:3000/d/reperibilita-main-v1',
    aggiornato_il TIMESTAMP DEFAULT NOW()
);

INSERT INTO impostazioni (
    costo_orario, costo_per_chiamata, costo_reperibilita_giornaliero,
    weekend_call_enabled, costo_orario_weekend, costo_per_chiamata_weekend,
    weekend_oncall_enabled, costo_reperibilita_weekend,
    lingua, grafana_url
) VALUES (25.00, 10.00, 50.00, FALSE, 25.00, 10.00, FALSE, 50.00, 'it', 'http://localhost:3000/d/reperibilita-main-v1');

-- Tabella configurazione Telegram
CREATE TABLE IF NOT EXISTS telegram_config (
    id SERIAL PRIMARY KEY,
    bot_token VARCHAR(200) DEFAULT '',
    chat_id VARCHAR(100) DEFAULT '',
    notifica_inizio BOOLEAN DEFAULT TRUE,
    notifica_fine BOOLEAN DEFAULT TRUE,
    abilitato BOOLEAN DEFAULT FALSE,
    aggiornato_il TIMESTAMP DEFAULT NOW()
);

INSERT INTO telegram_config (bot_token, chat_id, notifica_inizio, notifica_fine, abilitato)
VALUES ('', '', TRUE, TRUE, FALSE);

-- Tabella chiamate
CREATE TABLE IF NOT EXISTS chiamate (
    id SERIAL PRIMARY KEY,
    data_ora TIMESTAMP NOT NULL DEFAULT NOW(),
    durata_minuti INTEGER NOT NULL DEFAULT 0,
    descrizione TEXT,
    commessa VARCHAR(200),
    costo_calcolato DECIMAL(10,2) DEFAULT 0,
    creato_il TIMESTAMP DEFAULT NOW()
);

-- Tabella periodi di reperibilità
CREATE TABLE IF NOT EXISTS reperibilita (
    id SERIAL PRIMARY KEY,
    data_inizio DATE NOT NULL,
    data_fine DATE NOT NULL,
    note TEXT,
    costo_calcolato DECIMAL(10,2) DEFAULT 0,
    creato_il TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chiamate_data ON chiamate(data_ora);
CREATE INDEX IF NOT EXISTS idx_reperibilita_data ON reperibilita(data_inizio);
