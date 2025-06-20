# Phase Ω.5.5.2b — Chain Viewer Scaffold & Relay Path Playback

This micro-phase introduces a basic interface for visualizing relay chains.
Messages relayed between assistants can now be inspected step by step.

## View Routes
- `/relay/chains/:chainId` – inspect a relay chain and its delivery status.

## Components
- **RelayChainViewer.jsx** – renders the sequence of relay nodes.
- **RelayChainNodeCard.jsx** – displays metadata for each hop.

## Features
- Shows assistant hops with message text and symbolic tags.
- Status icons for pending, delivered or reflected nodes.
- Fallback indicators for skipped or timed-out hops.
- Uses mock data until backend endpoints are live.

---
Prepares for Phase Ω.5.5.3 — Assistant Execution Timeline Viewer, Symbolic Retry Loop Visualizer & Auto-Dispatch Chain Planner.
