import re


EQG_PIECE_ROOTS = {
	"root_body": "ROOT_BODY",
	"pelv": "PELV",
	"chest_chest01": "CHEST_CHEST01",
	"chest_chest02": "CHEST_CHEST02",
	"arml_clav": "ARML_CLAV",
	"armr_clav": "ARMR_CLAV",
	"arml_bcep": "ARML_BCEP",
	"armr_bcep": "ARMR_BCEP",
	"legl_thgh": "LEGL_THGH",
	"legr_thgh": "LEGR_THGH",
	"hair": "CHEST_CHEST03",
	"facialhair": "NECK_NECK",
	"facialatt": "HEAD_HEAD",
	"tattoo": "ROOT_BONE",
}


def eqg_piece_root(
	model_tag: str,
	race_tag: str,
) -> str | None:
	"""
	Return the attachment root for a standard multipart EQG model name.
	"""

	tag = str(model_tag or "").strip().casefold()
	race = str(race_tag or "").strip().casefold()

	if not race:
		return None

	# Standard armor:
	# dkm_03_00_arml_clav
	armor_match = re.fullmatch(
		rf"{re.escape(race)}_"
		rf"\d{{2}}_\d{{2}}_"
		rf"([a-z0-9_]+)",
		tag,
	)

	if armor_match is not None:
		return EQG_PIECE_ROOTS.get(
			armor_match.group(1)
		)

	# Customization:
	# dkm_hair_06
	# dkm_facialhair_03
	# dkm_facialatt_07
	customization_match = re.fullmatch(
		rf"{re.escape(race)}_"
		rf"(hair|facialhair|facialatt)_"
		rf"\d{{2}}",
		tag,
	)

	if customization_match is not None:
		return EQG_PIECE_ROOTS.get(
			customization_match.group(1)
		)

	# Tattoo geometry always uses model variation 00.
	if tag == f"{race}_tattoo_00":
		return EQG_PIECE_ROOTS["tattoo"]

	return None