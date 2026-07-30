-- PROCEDURE: public.bet_update()

-- DROP PROCEDURE IF EXISTS public.bet_update();

CREATE OR REPLACE PROCEDURE public.bet_update(
	)
LANGUAGE 'sql'

BEGIN ATOMIC
 UPDATE l4m_app_bet SET "IsExpired" = true
   WHERE (((l4m_app_bet."Expiration_Date")::timestamp without time zone AT TIME ZONE 'Europe/Rome'::text) <= (now() AT TIME ZONE 'Europe/Rome'::text));
 UPDATE l4m_app_bet SET "Carognata" = true
   WHERE (((l4m_app_bet."Expiration_Date")::timestamp without time zone AT TIME ZONE 'Europe/Rome'::text) <= ((now() AT TIME ZONE 'Europe/Rome'::text) - '-08:00:00'::interval));
END;

ALTER PROCEDURE public.bet_update()
    OWNER TO postgres;
