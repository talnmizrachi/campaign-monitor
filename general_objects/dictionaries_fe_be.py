
def get_be_criteria_for_campaign(fe_criteria):
	criteras = {
		"TypeForm Sent": "typeform_sent",
		"MQL": "mql",
		"SQL": "sql",
		"BG Enrolled": "bg_enrolled",
	}
	return criteras.get(fe_criteria)
