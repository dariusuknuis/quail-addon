# quail-addon

Compatible Quail version: 1.7-d
Recommended Blender Version: 5.0

Importing Assets

1) The archive you want to import by going to File>Import>EverQuest Archive
<img width="592" height="692" alt="image" src="https://github.com/user-attachments/assets/4b9578b9-d48e-4c99-9ecf-77fcc164f726" />
2) You can select a .s3d file, a .eqg file, or a .wce file. Selecting the _root.wce will load everything that _root.wce file references.
3) "Clear Scene Before Import" will delete basically everything from the scene. If you want to load additional archives after loading one already, you should uncheck this.

Exporting Assets

1) You can only export s3d/wld objects currently. Select the collection you want to export in the Outliner. Only collections are currently exportable at the moment.
2) Select the main collection to export everything contained in within. Select an individual collection, such as an ACTORDEF collection, to just export that one.
3) Go to File>Emport>EverQuest Archive.
4) Choose the Format. Any mode will export with image files, but the image files are currently always PNG, even if they have different file extensions.
<img width="1470" height="520" alt="image" src="https://github.com/user-attachments/assets/3b225b03-000e-4248-bd4b-7cf0662d956b" />



