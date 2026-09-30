USE foxxpi_database;

DELIMITER $$

CREATE EVENT IF NOT EXISTS evt_limpar_noticias_antigas
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    -- Remove notícias mais antigas que 30 dias
    DELETE FROM noticias 
    WHERE criado_em < NOW() - INTERVAL 30 DAY;
END $$

DELIMITER ;