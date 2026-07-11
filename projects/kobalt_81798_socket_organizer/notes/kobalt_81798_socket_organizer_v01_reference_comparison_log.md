# Kobalt 81798 Socket Organizer v01 Reference Comparison Log

## References Compared

- Official Lowe's product page for item #4103169 / model #81798.
- Official Lowe's Dimensions Guide PDF component list.
- User screenshots of an Etsy listing, used only as layout support and not copied as source geometry.

## Inventory Comparison

- Official inventory count: 153 pieces.
- Modeled pocket/channel count: 153.
- 1/4-in drive groups: 46 represented as 38 circular pockets plus 8 long channels.
- 3/8-in drive groups: 73 represented as 56 circular pockets plus 17 long channels.
- 1/2-in drive groups: 34 represented as 34 circular pockets.
- Result: PASS.

## Footprint / Zone Comparison

- Screenshot-derived overall footprint: 621.03 x 332.74 x 12.70 mm.
- SCAD reference layout parameters: 621.03 x 332.74 x 12.70 mm before raised labels.
- Left / center / right zone widths: 219.71 / 254.00 / 147.32 mm.
- Left split: 134.87 / 197.87 mm.
- Right split: 175.26 / 157.40 mm.
- Center split: 166.37 mm.
- Result: PASS against supporting footprint dimensions.

## Top Silhouette Comparison

- v01 preserves the asymmetric left, center, and right zone structure shown in the screenshots.
- Center modules contain two banks of long channels: 12 upper and 13 lower.
- Left-top carries the 1/2DR groups.
- Left-bottom carries selected 3/8DR shallow/external/short hex groups.
- Right-top carries the 1/4DR non-long groups.
- Right-bottom carries 3/8DR Torx, tamper-proof Torx, and screwdriver groups.
- Result: PASS for functional grouping and count; exact seller styling was not copied.

## Front / Side Silhouette Comparison

- Supporting side screenshot shows a thin tray around 0.50 in / 12.70 mm.
- v01 base thickness is 12.70 mm with raised labels bringing exported module Z to about 13.15 mm.
- Pockets and channels are blind from the top; bottom remains flat for drawer/bench use.
- Result: PASS.

## Critical Local Features

- Socket cups: circular blind recesses with chamfered mouths.
- Long bits: rounded channels with collar pockets near one end.
- Labels: shallow raised parametric stroke labels, no logos.
- Module joins: original continuous flat tabs and clearance sockets, not copied from a commercial STL.
- Result: PASS for v01 functional geometry, with fit confidence limited by estimated ODs.

## Mismatches / Limits

- Exact socket body ODs are not available and remain low confidence.
- The Etsy screenshot was used only for layout support; v01 does not copy seller-specific decorative geometry.
- `right_top` verified STL extents are smaller than nominal zone width because its left-edge alignment socket is an open clearance socket; the neighboring center module tab fills that seam in assembly.
