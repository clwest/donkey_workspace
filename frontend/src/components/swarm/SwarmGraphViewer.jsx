import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import apiFetch from "../../utils/apiClient";

export default function SwarmGraphViewer() {
  const [graph, setGraph] = useState(null);
  const ref = useRef();

  useEffect(() => {
    apiFetch("/swarm/graph/")
      .then(setGraph)
      .catch(() => setGraph(null));
  }, []);

  useEffect(() => {
    if (!graph) return;
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();
    const nodes = graph.nodes || [];
    const links = graph.edges || [];
    const width = 600;
    const height = 400;
    const sim = d3
      .forceSimulation(nodes)
      .force("link", d3.forceLink(links).distance(80).id((d) => d.id))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#999");

    const node = svg
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", 10)
      .attr("fill", "#0d6efd");

    const label = svg
      .append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text((d) => d.name || d.id)
      .attr("font-size", 10)
      .attr("dx", 12)
      .attr("dy", 4);

    sim.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);
      node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
      label.attr("x", (d) => d.x).attr("y", (d) => d.y);
    });
  }, [graph]);

  if (!graph) return <div>Loading graph...</div>;
  return <svg ref={ref} width={600} height={400}></svg>;
}
