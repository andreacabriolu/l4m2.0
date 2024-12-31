CREATE PROCEDURE bet_update()
LANGUAGE SQL
BEGIN ATOMIC
  	update public.l4m_app_bet
	set "IsExpired"=true
	where Cast(l4m_app_bet."Expiration_Date" as timestamp) <= NOW();
END;