import { useEffect, useRef } from "react";
import * as d3 from "d3";
import apiFetch from "../../utils/apiClient";

export default function BeliefClusterMap() {
  const ref = useRef();

  useEffect(() => {
    apiFetch("/agents/belief-clusters/")
      .then((clusters) => {
        const nodes = [];
        const links = [];
        clusters.forEach((c, i) => {
          const clusterId = `cluster-${i}`;
          nodes.push({ id: clusterId, type: "cluster" });
          (c.assistants || []).forEach((a) => {
            nodes.push({ id: a, type: "assistant" });
            links.push({ source: clusterId, target: a });
          });
        });

        const svg = d3.select(ref.current);
        svg.selectAll("*").remove();
        const width = 400;
        const height = 300;
        const sim = d3
          .forceSimulation(nodes)
          .force("link", d3.forceLink(links).distance(60).id((d) => d.id))
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
          .attr("fill", (d) => (d.type === "cluster" ? "#007bff" : "#ccc"));

        const label = svg
          .append("g")
          .selectAll("text")
          .data(nodes)
          .enter()
          .append("text")
          .text((d) => d.id)
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
      })
      .catch(() => {});
  }, []);

  return <svg ref={ref} width={400} height={300}></svg>;
}
