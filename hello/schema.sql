CREATE TABLE IF NOT EXISTS visit_count (
    id SERIAL PRIMARY KEY,
    count INTEGER NOT NULL
);
INSERT INTO visit_count (id, count) 
VALUES (1, 0) 
ON CONFLICT (id) 
DO NOTHING;
