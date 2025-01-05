CREATE PROCEDURE bet_update()
LANGUAGE SQL
BEGIN ATOMIC
  	update public.l4m_app_bet
	set "IsExpired"=true
	where Cast(l4m_app_bet."Expiration_Date" as timestamp) <= NOW();

	update public.l4m_app_bet
	set "Carognata"=true
	where Cast(l4m_app_bet."Expiration_Date" as timestamp) <= NOW() - INTERVAL '0 DAY - 12 HOURS' ;
END;