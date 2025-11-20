INSERT INTO public.l4m_app_team_competition(
	"Elimination_stage", "Competition_id", "Team_id")
select '',"s"."Competition_id",ts.team_id from "l4m_app_team_Series" ts join "l4m_app_series" s on "ts"."series_id"="s".id 
;