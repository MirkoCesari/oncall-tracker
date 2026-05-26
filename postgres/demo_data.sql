-- Demo data for screenshots — run against an already-initialized database.
-- Clears existing call/on-call data and repopulates with 6 months of realistic entries.

TRUNCATE TABLE chiamate, reperibilita RESTART IDENTITY;

UPDATE impostazioni SET lingua = 'en';

-- ─── ON-CALL PERIODS (7 days each @ €50/day = €350.00) ───────────────────────

INSERT INTO reperibilita (data_inizio, data_fine, note, costo_calcolato, creato_il) VALUES
  ('2025-11-17', '2025-11-23', 'Primary on-call rotation',                     350.00, '2025-11-17'),
  ('2025-12-01', '2025-12-07', 'Holiday coverage — December',                  350.00, '2025-12-01'),
  ('2025-12-22', '2025-12-28', 'Christmas on-call rotation',                   350.00, '2025-12-22'),
  ('2026-01-05', '2026-01-11', 'January rotation — week 2',                    350.00, '2026-01-05'),
  ('2026-01-26', '2026-02-01', 'End-of-month coverage',                        350.00, '2026-01-26'),
  ('2026-02-16', '2026-02-22', 'February rotation',                            350.00, '2026-02-16'),
  ('2026-03-09', '2026-03-15', 'March rotation',                               350.00, '2026-03-09'),
  ('2026-04-06', '2026-04-12', 'April rotation — week 2',                      350.00, '2026-04-06'),
  ('2026-04-27', '2026-05-03', 'April/May transition coverage',                350.00, '2026-04-27'),
  ('2026-05-11', '2026-05-17', 'May rotation',                                 350.00, '2026-05-11');

-- ─── CALLS ───────────────────────────────────────────────────────────────────
-- Cost formula: round((duration_min / 60.0) * 25 + 10, 2)

INSERT INTO chiamate (data_ora, durata_minuti, descrizione, commessa, costo_calcolato, creato_il) VALUES

  -- November 2025 (3 calls)
  ('2025-11-18 02:15', 30, 'Database replication lag detected',                    'INC-8741',    22.50, '2025-11-18 02:15'),
  ('2025-11-19 14:30', 15, 'SSL certificate expiry warning',                       'WO-2025-047', 16.25, '2025-11-19 14:30'),
  ('2025-11-22 09:45', 45, 'Load balancer health check failure',                   'INC-8803',    28.75, '2025-11-22 09:45'),

  -- December 2025 (4 calls)
  ('2025-12-02 22:10', 60, 'API gateway timeout — upstream service unavailable',   'INC-9012',    35.00, '2025-12-02 22:10'),
  ('2025-12-04 03:30', 20, 'Disk space alert on production server',                'WO-2025-055', 18.33, '2025-12-04 03:30'),
  ('2025-12-23 01:00', 90, 'Total service outage — emergency database failover',   'INC-9241',    47.50, '2025-12-23 01:00'),
  ('2025-12-26 16:20', 10, 'False alarm — monitoring misconfiguration',            'WO-2025-061', 14.17, '2025-12-26 16:20'),

  -- January 2026 (5 calls)
  ('2026-01-06 23:45', 35, 'Memory leak in payment service',                       'INC-9344',    24.58, '2026-01-06 23:45'),
  ('2026-01-08 07:15', 25, 'CI/CD pipeline stuck — manual restart required',       'WO-2026-003', 20.42, '2026-01-08 07:15'),
  ('2026-01-10 13:00', 50, 'Data migration rollback after integrity check failure','INC-9401',    30.83, '2026-01-10 13:00'),
  ('2026-01-27 04:20', 75, 'Kubernetes pod crash loop in production namespace',    'INC-9512',    41.25, '2026-01-27 04:20'),
  ('2026-01-29 18:30', 15, 'CDN cache purge request from client',                  'WO-2026-009', 16.25, '2026-01-29 18:30'),

  -- February 2026 (4 calls)
  ('2026-02-17 01:50', 40, 'Network partition — datacenter connectivity lost',     'INC-9631',    26.67, '2026-02-17 01:50'),
  ('2026-02-18 22:00',120, 'Full backup restore drill — ransomware prevention',    'WO-2026-018', 60.00, '2026-02-18 22:00'),
  ('2026-02-20 09:10', 20, 'Authentication service degraded performance',          'INC-9702',    18.33, '2026-02-20 09:10'),
  ('2026-02-21 15:45',  8, 'Alert noise — acknowledged and auto-closed',           'WO-2026-021', 13.33, '2026-02-21 15:45'),

  -- March 2026 (4 calls)
  ('2026-03-10 00:30', 55, 'Redis cluster split-brain — manual intervention',      'INC-9815',    32.92, '2026-03-10 00:30'),
  ('2026-03-11 11:20', 30, 'Scheduled maintenance window overrun',                 'WO-2026-029', 22.50, '2026-03-11 11:20'),
  ('2026-03-12 21:00', 45, 'Storage I/O saturation on database host',              'INC-9867',    28.75, '2026-03-12 21:00'),
  ('2026-03-14 03:15', 15, 'DNS resolution failure — external zone',               'WO-2026-033', 16.25, '2026-03-14 03:15'),

  -- April 2026 (5 calls)
  ('2026-04-07 02:00', 60, 'Database deadlock in batch processing job',            'INC-9944',    35.00, '2026-04-07 02:00'),
  ('2026-04-09 17:30', 25, 'TLS handshake errors — certificate mismatch',          'WO-2026-041', 20.42, '2026-04-09 17:30'),
  ('2026-04-11 23:50', 35, 'Webhook delivery failures — queue backlog',            'INC-9981',    24.58, '2026-04-11 23:50'),
  ('2026-04-28 08:45', 20, 'Container registry pull rate limit exceeded',          'WO-2026-049', 18.33, '2026-04-28 08:45'),
  ('2026-04-30 14:00', 50, 'Elasticsearch cluster yellow — shard reallocation',    'INC-0034',    30.83, '2026-04-30 14:00'),

  -- May 2026 (5 calls)
  ('2026-05-12 01:30', 45, 'Microservice circuit breaker open — downstream timeout','INC-0112',   28.75, '2026-05-12 01:30'),
  ('2026-05-13 22:10', 15, 'Log ingestion pipeline stalled',                       'WO-2026-055', 16.25, '2026-05-13 22:10'),
  ('2026-05-15 04:45', 30, 'VM snapshot job failure — storage backend error',      'INC-0134',    22.50, '2026-05-15 04:45'),
  ('2026-05-16 13:20', 10, 'False positive — auto-resolved by monitoring system',  'WO-2026-058', 14.17, '2026-05-16 13:20'),
  ('2026-05-21 03:00', 90, 'Production DB slow queries — emergency index rebuild', 'INC-0178',    47.50, '2026-05-21 03:00');
