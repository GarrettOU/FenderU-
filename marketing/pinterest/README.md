# Pinterest re-pin, 9 Nov 2026

Audit (`audit-2026-11-09.md`): 142 live pins on the FenderU boards, 95 carry banned copy in the
description ("$119 the pair" 92, "matched pair" 28, "port and starboard" 17, "48 hours" 2, "$99" 1,
"every dock", "show your colors", "fly the flag" 1 each, literal "null" from a broken Make variable in
31). Titles are all clean. Four of five board descriptions also carry banned copy. Pins cannot be
edited, so each flagged pin is re-created with a corrected description and the old one deleted
(standing rule 0c).

`repin-2026-11-09.json`: the 95 replacements. Each item: `pin_id` (the old pin to delete), `board_id`,
`title` (unchanged), `description` (rebuilt from approved facts only: "$119 for the two-pack",
"Sold as a 2-pack", the fit list, UPS with tracking; every banned sentence removed; zero banned hits
on re-check), `image` (the pin's own full-size image). Create first, then delete, so nothing is lost.

`board-descriptions-2026-11-09.json`: replacement text for the four boards (edit in place, no delete).

Make scenario 6649690 ("FenderU - replace pins carrying banned lines") holds a 5-pin pilot of this set
as its blueprint: Iterator over the array, then pinterest:createPin, then pinterest:deletePin. Make
allows two active scenarios; deactivate 6229425 (Pinterest pins) for the run and reactivate it after,
never 6374100 (order alert).

Run order: pilot (5) and verify on the public boards; then the remaining 90 in batches of 15 to 20
(replace the Iterator array); then the four board PATCHes (`/v5/boards/{id}`, body `{"description": ...}`).
The Head session was refused permission to activate the scenario, so a person clicks Run in Make or
grants the permission; the Head verifies after each batch by reading the public board feeds.
