# Phase 6.5 — Memory Portals, Mythfield Rendering & Symbolic Compression

Phase 6.5 adds direct access to targeted memory, visual narrative maps and techniques for compressing cross-thread stories. These features build on the existing agent architecture and prepare the swarm for more advanced knowledge sharing.

## Core Features

### MemoryPortal
```
class MemoryPortal(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    entry_points = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_focus = models.TextField()
    access_scope = models.CharField(max_length=100)  # self, guild, public
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Creates scoped gateways into memory streams or specific narrative events.

### MythfieldRender
```
class MythfieldRender(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    narrative_focus = models.TextField()
    purpose_alignment_vector = models.JSONField()
    symbolic_map_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Visualizes belief topographies and reflective terrain for planning or swarm navigation.

### SymbolicCompressionPacket
```
class SymbolicCompressionPacket(models.Model):
    name = models.CharField(max_length=150)
    source_threads = models.ManyToManyField(CollaborationThread)
    compressed_summary = models.TextField()
    myth_tags = models.JSONField()
    embedding_vector = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)
```
Optimizes multi-threaded memory into transferable symbolic form.

## API Endpoints
- `/api/memory-portals/` — create and query contextual memory windows
- `/api/mythfield-renders/` — explore symbolic landscape data
- `/api/symbolic-compression/` — store and reuse compressed memory capsules

## React Components
- `MemoryPortalViewer.jsx` — navigate assistant memory portals
- `MythfieldRenderer.jsx` — visualize intent flow and symbolic weight
- `CompressionPacketLibrary.jsx` — browse and reuse compressed packets

## Testing Goals
- Portals correctly filter and expose memory entries by scope
- Mythfield rendering aligns with an assistant's narrative purpose
- Symbolic packets can compress thread data and recover intent context

Phase 6.5 prepares for **Phase 6.6** which introduces multi-agent broadcasting and symbol-weighted learning.
