import bpy, re
from bpy_extras import anim_utils


S3D_TO_EQG_ANIMATIONS = {
	"C01": "KICK",
	"C02": "STPR",
	"C03": "SL2H",
	"C04": "ST2H",
	"C05": "SLPR",
	"C06": "SLSC",
	"C07": "BASH",
	"C08": "PATK",
	"C09": "BATK",
	"C10": "WATK",
	"C11": "RKCK",
	"D01": "FLCH",
	"D02": "MSHT",
	"D03": "FLDM",
	"D04": "SPAS",
	"D05": "CRMP",
	"L01": "WALK",
	"L02": "NRUN",
	"L03": "JMPA",
	"L04": "JMPU",
	"L05": "FALL",
	"L06": "CWLK",
	"L07": "CLMB",
	"L08": "CRCH",
	"L09": "TWTR",
	"L10": "NRUN_MT",
	"O01": "IDLA",
	"O02": "IDLE",
	"P01": "STDA",
	"P02": "STNG",
	"P03": "TURN",
	"P04": "LTRN",
	"P05": "KNEL",
	"P06": "SWIM",
	"P07": "NSIT",
	"P08": "STND",
	"P09": "STND_MT",
	"S01": "TRIU",
	"S02": "AGNY",
	"S03": "WAVE",
	"S04": "NGTV",
	"S05": "BORD",
	"S06": "HNOD",
	"S08": "PRAY",
	"S09": "CLAP",
	"S10": "DOVR",
	"S11": "BLSH",
	"S12": "LAGH",
	"S13": "COGH",
	"S14": "CRNG",
	"S15": "TILT",
	"S16": "DNCE",
	"S17": "HSHK",
	"S18": "HIPS",
	"S19": "STRE",
	"S20": "SKNL",
	"S21": "HLGH",
	"S22": "NPNT",
	"S23": "SHRG",
	"S24": "RAIS",
	"S25": "SLTE",
	"S26": "SHVR",
	"S27": "IMPT",
	"S28": "NBOW",
	"S29": "SMLE",
	"T01": "DRUM",
	"T02": "LUTE",
	"T03": "HORN",
	"T04": "DCST",
	"T05": "GCST",
	"T06": "MCST",
	"T07": "MKCK",
	"T08": "MHA1",
	"T09": "MHA2",
}


def _eqg_animation_name(action_name, race_tag):
	name = str(action_name or "").strip()
	race = str(race_tag or "").strip()

	match = re.fullmatch(
		rf"([CDLOPST]\d{{2}})_{re.escape(race)}",
		name,
		re.IGNORECASE,
	)

	if match is None:
		return None

	source_code = match.group(1).upper()
	mapped = S3D_TO_EQG_ANIMATIONS.get(source_code)

	if mapped is None:
		return None

	if mapped.endswith("_MT"):
		animation_code = mapped[:-3]
		animation_type = "mt"
	else:
		animation_code = mapped
		animation_type = "ba"

	return (
		f"{animation_code.lower()}_"
		f"{animation_type}_1_"
		f"{race.lower()}"
	)


def _race_tag_from_armature(obj):
	suffix = "_HS_DEF"

	if not obj.name.casefold().endswith(suffix.casefold()):
		return None

	race_tag = obj.name[:-len(suffix)]

	if not race_tag:
		return None

	return race_tag


def _exact_bone_names(race_tag, has_abdomen):
	chest_name = (
		"CHEST_CHEST02"
		if has_abdomen
		else "CHEST_CHEST01"
	)

	result = {
		f"{race_tag}_DAG": "ROOT_BONE",
		f"{race_tag}PE_DAG": "PELV",
		f"{race_tag}TH_R_DAG": "LEGR_THGH",
		f"{race_tag}CA_R_DAG": "LEGR_CALF",
		f"{race_tag}BO_R_DAG": "LEGR_FOOT",
		f"{race_tag}TO_R_DAG": "LEGR_TOE01",
		f"{race_tag}TH_L_DAG": "LEGL_THGH",
		f"{race_tag}CA_L_DAG": "LEGL_CALF",
		f"{race_tag}BO_L_DAG": "LEGL_FOOT",
		f"{race_tag}TO_L_DAG": "LEGL_TOE01",
		f"{race_tag}CH_DAG": chest_name,
		f"{race_tag}NE_DAG": "NECK_NECK",
		f"{race_tag}HE_DAG": "HEAD_HEAD",
		f"{race_tag}HEAD_POINT_DAG": "HEAD_NAME",
		f"{race_tag}BI_L_DAG": "ARML_BCEP",
		f"{race_tag}FO_L_DAG": "ARML_FARM",
		f"{race_tag}FI_L_DAG": "ARML_HAND",
		f"{race_tag}L_POINT_DAG": "ARML_WEAP",
		f"{race_tag}SHIELD_POINT_DAG": "ARML_SHLD",
		f"{race_tag}BI_R_DAG": "ARMR_BCEP",
		f"{race_tag}FO_R_DAG": "ARMR_FARM",
		f"{race_tag}FI_R_DAG": "ARMR_HAND",
		f"{race_tag}R_POINT_DAG": "ARMR_WEAP",
	}

	if has_abdomen:
		result[f"{race_tag}AB_DAG"] = "CHEST_CHEST01"

	return result


def _parent_prefix(parent_name):
	if "_" in parent_name:
		return parent_name.split("_", 1)[0] + "_"

	return parent_name + "_"


def _strip_s3d_bone_name(name, race_tag):
	result = name

	if result.casefold().startswith(race_tag.casefold()):
		result = result[len(race_tag):]

	if result.casefold().endswith("_dag"):
		result = result[:-4]

	return result.lstrip("_")


def _build_bone_rename_map(armature_obj, race_tag):
	armature = armature_obj.data
	abdomen_name = f"{race_tag}AB_DAG"

	has_abdomen = any(
		bone.name.casefold() == abdomen_name.casefold()
		for bone in armature.bones
	)

	exact_names = {
		old_name.casefold(): new_name
		for old_name, new_name in _exact_bone_names(
			race_tag,
			has_abdomen,
		).items()
	}

	rename_map = {}
	pending = list(armature.bones)

	while pending:
		progress = False

		for bone in list(pending):
			if bone.parent is not None and bone.parent.name not in rename_map:
				continue

			exact_name = exact_names.get(
				bone.name.casefold()
			)

			if exact_name is not None:
				new_name = exact_name

			else:
				remainder = _strip_s3d_bone_name(
					bone.name,
					race_tag,
				)

				if bone.parent is not None:
					parent_name = rename_map[
						bone.parent.name
					]
					new_name = (
						_parent_prefix(parent_name)
						+ remainder
					)
				else:
					new_name = remainder

			rename_map[bone.name] = new_name
			pending.remove(bone)
			progress = True

		if not progress:
			return None, "Could not resolve the armature hierarchy"

	target_names = {}

	for old_name, new_name in rename_map.items():
		key = new_name.casefold()

		if key in target_names:
			return None, (
				f"Both {target_names[key]} and {old_name} "
				f"would be renamed to {new_name}"
			)

		target_names[key] = old_name

	return rename_map, ""


def _uses_armature(obj, armature_obj):
	if obj.type != 'MESH':
		return False

	if obj.parent == armature_obj:
		return True

	return any(
		modifier.type == 'ARMATURE'
		and modifier.object == armature_obj
		for modifier in obj.modifiers
	)


def _merge_vertex_group(obj, old_name, new_name):
	source = obj.vertex_groups.get(old_name)

	if source is None or old_name == new_name:
		return

	target = obj.vertex_groups.get(new_name)

	if target is None:
		source.name = new_name
		return

	source_index = source.index

	for vertex in obj.data.vertices:
		for assignment in vertex.groups:
			if assignment.group == source_index:
				target.add(
					[vertex.index],
					assignment.weight,
					'ADD',
				)
				break

	obj.vertex_groups.remove(source)


def _rename_vertex_groups(armature_obj, rename_map):
	for obj in bpy.data.objects:
		if not _uses_armature(obj, armature_obj):
			continue

		for old_name, new_name in rename_map.items():
			_merge_vertex_group(
				obj,
				old_name,
				new_name,
			)


def _matching_actions(race_tag):
	race_lower = race_tag.casefold()

	for action in bpy.data.actions:
		if action.name.casefold().endswith(race_lower):
			yield action


def _replace_bone_path(data_path, old_name, new_name):
	old_identifier = bpy.utils.escape_identifier(old_name)
	new_identifier = bpy.utils.escape_identifier(new_name)

	old_path = f'pose.bones["{old_identifier}"]'
	new_path = f'pose.bones["{new_identifier}"]'

	return data_path.replace(old_path, new_path)


def _rename_action_bones(action, rename_map):
	for slot in action.slots:
		channelbag = anim_utils.action_get_channelbag_for_slot(
			action,
			slot,
		)

		if channelbag is None:
			continue

		for fcurve in channelbag.fcurves:
			data_path = fcurve.data_path

			for old_name, new_name in rename_map.items():
				data_path = _replace_bone_path(
					data_path,
					old_name,
					new_name,
				)

			fcurve.data_path = data_path

		for group in channelbag.groups:
			new_name = rename_map.get(group.name)

			if new_name is not None:
				group.name = new_name

	for track_props in action.quail_tracks:
		new_name = rename_map.get(track_props.tag)

		if new_name is not None:
			track_props.tag = new_name


def _rename_animations(race_tag, rename_map):
	actions = list(_matching_actions(race_tag))

	for action in actions:
		_rename_action_bones(action, rename_map)

		new_name = _eqg_animation_name(
			action.name,
			race_tag,
		)

		if new_name is not None:
			action.name = new_name


def convert_s3d_to_eqg_armature(armature_obj):
	if armature_obj is None:
		return "Object is None"

	if armature_obj.type != 'ARMATURE':
		return f"{armature_obj.name} is not an armature"

	if armature_obj.get("quaildef") != "hierarchicalspritedef":
		return (
			f"{armature_obj.name} is not a "
			"HIERARCHICALSPRITEDEF"
		)

	race_tag = _race_tag_from_armature(armature_obj)

	if race_tag is None:
		return (
			f"Armature name {armature_obj.name} does not end "
			f"with _HS_DEF"
		)

	rename_map, err = _build_bone_rename_map(
		armature_obj,
		race_tag,
	)

	if err:
		return err

	_rename_vertex_groups(
		armature_obj,
		rename_map,
	)

	_rename_animations(
		race_tag,
		rename_map,
	)

	for old_name, new_name in rename_map.items():
		bone = armature_obj.data.bones.get(old_name)

		if bone is not None:
			bone.name = new_name

	new_armature_name = f"{race_tag}_armature"

	armature_obj.name = new_armature_name
	armature_obj.data.name = new_armature_name
	armature_obj["quaildef"] = "eqgmodarmature"

	return ""


class OBJECT_OT_convert_s3d_to_eqg_armature(bpy.types.Operator):
	bl_idname = "object.convert_s3d_to_eqg_armature"
	bl_label = "Convert to EQG Armature"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.object

		return (
			obj is not None
			and obj.type == 'ARMATURE'
			and obj.get("quaildef")
			== "hierarchicalspritedef"
		)

	def execute(self, context):
		obj = context.object
		err = convert_s3d_to_eqg_armature(obj)

		if err:
			self.report({'ERROR'}, err)
			return {'CANCELLED'}

		self.report(
			{'INFO'},
			f"Converted {obj.name} to an EQG armature",
		)

		return {'FINISHED'}


def draw_armature_conversion_in_transform(self, context):
	obj = context.object

	if (
		obj is None
		or obj.type != 'ARMATURE'
		or obj.get("quaildef")
		!= "hierarchicalspritedef"
	):
		return

	box = self.layout.box()
	box.label(
		text="Convert Armature",
		icon='ARMATURE_DATA',
	)

	box.operator(
		"object.convert_s3d_to_eqg_armature",
		text="Convert to EQG Armature",
	)


def register():
	bpy.types.OBJECT_PT_transform.append(
		draw_armature_conversion_in_transform
	)


def unregister():
	try:
		bpy.types.OBJECT_PT_transform.remove(
			draw_armature_conversion_in_transform
		)
	except ValueError:
		pass