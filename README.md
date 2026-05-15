# quail-addon

Compatible Quail version: `1.7-d`  
Recommended Blender version: `5.0`

---

# Importing Assets

## 1. Open the Import Menu

Go to:

`File > Import > EverQuest Archive`

<img width="592" height="692" alt="Import Menu" src="https://github.com/user-attachments/assets/4b9578b9-d48e-4c99-9ecf-77fcc164f726" />

---

## 2. Select an Archive

You can import:

- `.s3d`
- `.eqg`
- `.wce`

Selecting `_root.wce` will automatically load everything referenced by that file.

---

## 3. Clear Scene Before Import

**Clear Scene Before Import** will delete most existing objects in the scene.

If you want to load additional archives after importing one already, leave this option unchecked.

---

# Exporting Assets

## 1. Select a Collection

Currently, only **collections** can be exported.

In the Outliner:

- Select the main collection to export everything inside it.
- Select a specific collection (such as an `ACTORDEF` collection) to export only that asset set.

---

## 2. Open the Export Menu

Go to:

`File > Export > EverQuest Archive`

> NOTE: The menu item currently says `Emport` in the add-on UI.

---

## 3. Choose an Export Format

Any export mode will also export image files.

Currently, all exported textures are written as PNG files, even if they use different file extensions.

<img width="1470" height="520" alt="Export Options" src="https://github.com/user-attachments/assets/3b225b03-000e-4248-bd4b-7cf0662d956b" />

---

