# quail-addon

Compatible Quail version: `1.7-d`  
Recommended Blender version: `5.0`

---

# Importing Assets

## 1. Open the Import Menu

Go to:

`File > Import > EverQuest Archive`

<img width="291" height="346" alt="Import Menu" src="https://github.com/user-attachments/assets/4b9578b9-d48e-4c99-9ecf-77fcc164f726" />

## 2. Select an Archive

You can import:

- `.s3d`
- `.eqg`
- `.wce`

Selecting `_root.wce` will automatically load everything referenced by that file.

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

## 2. Open the Export Menu

Go to:

`File > Export > EverQuest Archive`

## 3. Choose an Export Format

Any export mode will also export image files.

Currently, all exported textures are written as PNG files, even if they use different file extensions.

<img width="735" height="260" alt="Export Options" src="https://github.com/user-attachments/assets/3b225b03-000e-4248-bd4b-7cf0662d956b" />

---

# Loading Zones with objects

Zones load with dummy actor instances and rgbdeformation tracks, but if you load the {zone name}_obj file that is associated with the zone, first, loading the zone itself will make proper object instances for them.

<img width="701" height="362" alt="image" src="https://github.com/user-attachments/assets/c27da643-c88d-4cf9-9034-e499bb802de5" />

>Note: Object instances should be placed and moved with the actor instance objects, not with the mesh objects. 

---

# Panel Interfaces

Objects have panels related to their WCE properties. The location of each panel depends on their object type. Most panels can be accessed from one of the tabs in the Properties editor window. **In general, try to use the panels to adjust properties of objects, instead of other menus.**

---

# Quail Toolbar

This can be reached by pressing N in the 3D Viewport. Some options will only appear when certain objects types are selected and/or in certain modes. 

---


