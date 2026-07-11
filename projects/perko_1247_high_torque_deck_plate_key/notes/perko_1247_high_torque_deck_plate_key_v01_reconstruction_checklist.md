# Reconstruction Checklist

- [x] exact target part defined
- [x] reused surrounding parts defined
- [x] not-modeled items defined
- [x] reference hierarchy recorded
- [x] authoritative references recorded
- [x] supporting references recorded
- [x] anchor dimensions recorded
- [x] measured dimensions separated from inferred dimensions
- [x] protected interfaces recorded
- [x] rough mesh inspected if present
- [x] rough mesh treated as supporting only unless explicitly trusted
- [x] measurement checklist created if critical data is missing
- [x] bbox compared
- [x] side silhouette compared
- [x] front silhouette compared
- [x] top silhouette compared when needed
- [x] critical local features compared
- [x] reinforcement limited to non-interface zones where practical
- [x] print orientation chosen
- [x] support plan chosen
- [x] low-confidence zones documented
- [x] FDM printability reviewed
- [x] STL exported successfully or export failure documented
- [x] required previews rendered or render failure documented
- [x] versioned files named correctly

## Notes

- There was no rough mesh to inspect.
- BBox and silhouettes are model-controlled because no measured OEM model, photo scale, or CAD reference was supplied.
- The printed root relief collar is a non-mating strength feature; verify cap-face clearance before using high torque.
