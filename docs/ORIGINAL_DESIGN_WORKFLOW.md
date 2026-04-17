# Original Design Workflow

Use this workflow for true greenfield parts that are not tied to an existing reference part.

## Steps

1. Define the use case and functional requirements.
2. Explore concepts if that will improve the result.
3. Choose a concept if multiple directions were explored.
4. Plan the main parameters and modules.
5. Build clean OpenSCAD geometry.
6. Validate printability for the intended process.
7. Export versioned outputs, including STL.

## Notes

- Concept generation is optional, not mandatory, if the solution is obvious.
- Keep geometry readable and parametric.
- Record print orientation, support expectations, and key assumptions in notes.
- STL export is expected at completion unless export fails for a real technical reason.
- If the job later becomes reference-driven, switch task mode instead of forcing original design workflow onto it.
