> Earlier model revision. See [v2](../v2/README.md) for the revised wheels and camera.

# Rover — Blender model

This is an editable, photo-referenced reconstruction of your rover using the four original IMG_8361–IMG_8364 photographs.

## Files

- `Rover.blend` — master Blender scene, separate components, materials, four studio cameras; original private reference photographs removed.
- `Rover.glb` — portable model for other 3D software and web viewers. Includes the rover only, without the studio floor, lights or reference photographs.
- `Rover-Hero.png`, `Rover-Rear.png`, `Rover-Side.png`, `Rover-Top.png` — renders produced in Blender.
- `build_rover.py` — reproducible Blender Python construction script.
- `model-info.json` — scene version, object count and estimated bounding dimensions.

## Editing in Blender

Open `Rover.blend`. The numbered collections separate the chassis, wheels, Pi board, webcam, cables, markings and studio. Move the entire rover with the root empty named **ROVER | move the complete model**. Each wheel has a separate pivot at its axle; rotate its local X axis to spin the wheel.

The four named cameras provide hero, rear, side and top views. Cable curves and label text remain editable in the `.blend` file. The GLB converts these to meshes for portability.

## Scale and fidelity

Dimensions are estimated, as requested, using a nominal 85 × 56 mm Raspberry Pi board as a scale reference. The scene uses metres and displays millimetres. See `model-info.json` for the model's full bounding dimensions, including cables. Tires, chassis silhouette, camera, board, cable loops and red tie are modeled from the visible photos. Small electronics and unseen underside details are simplified. This is a visualization model, not a measured CAD model or a fabrication file.

## Rebuilding

Created in Blender 4.5 LTS. Run from a terminal with Blender available:

```sh
blender --background --python build_rover.py
```

The script rebuilds the files in its own folder. Use `-- --draft` for a smaller hero render or `-- --no-render` to write model files only. Optional private reference JPEGs can be supplied through `ROVER_REFERENCE_DIR`; the public `.blend` contains no reference photographs.

Blender: https://www.blender.org/releases/4-5/

## Public repository copy

Original room photographs and their reference objects were removed from the Blender files. Modeled geometry and product renders are unchanged.
