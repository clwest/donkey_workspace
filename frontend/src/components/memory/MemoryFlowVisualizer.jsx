import { useEffect, useRef } from "react";
import * as d3 from "d3";

export default function MemoryFlowVisualizer({ data }) {
  const ref = useRef();

  useEffect(() => {
    if (!data) return;
    const nodes = data.nodes.map((n) => ({ ...n }));
    const links = data.edges.map((e) => ({ ...e }));
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();
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
      .attr("r", 8)
      .attr("fill", "#007bff")
      .call(
        d3
          .drag()
          .on("start", (event) => {
            if (!event.active) sim.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
          })
          .on("drag", (event) => {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
          })
          .on("end", (event) => {
            if (!event.active) sim.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
          })
      );

    const label = svg
      .append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text((d) => d.text)
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
  }, [data]);

  return <svg ref={ref} width={600} height={400}></svg>;
}
