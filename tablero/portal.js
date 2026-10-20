"use strict";

const byId = id => document.getElementById(id);
const labels = {pendiente: "Pendiente", en_ejecucion: "En ejecución", bloqueado: "Bloqueado", esperando_aprobacion: "Espera aprobación", completado: "Completado", omitido: "Omitido"};
let stages = [], projects = [], previousProjects = "", refreshing = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = String(text);
  return node;
}
function statusBadge(status, text) {
  return element("span", `status ${status}`, text || labels[status] || status);
}
function showNotice(message) {
  byId("notice").hidden = !message;
  byId("notice").textContent = message;
}
function commandButton(command) {
  const button = element("button", "command");
  button.type = "button";
  button.setAttribute("aria-label", `Copiar comando ${command}`);
  button.append(element("code", "", command), element("span", "", "Copiar"));
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(command);
      button.lastChild.textContent = "Copiado ✓";
      setTimeout(() => {button.lastChild.textContent = "Copiar";}, 1600);
    } catch {
      showNotice(`Copia este comando en el chat: ${command}`);
    }
  });
  return button;
}
function route() {
  try {return location.hash.slice(1).split("/").map(decodeURIComponent);}
  catch {return ["manual"];}
}
function stageDetail(stage, project) {
  const wrapper = element("div", "detail");
  const heading = element("div", "detail-heading");
  const headingText = element("div");
  headingText.append(element("h2", "", stage.title), element("p", "", `${stage.actor} · ${stage.summary}`));
  heading.append(element("span", "detail-num", stage.number), headingText);
  wrapper.append(heading);
  if (project) {
    const current = project.steps[stage.id];
    const context = element("div", "project-context");
    context.append(statusBadge(current.status), document.createTextNode(` · Intentos: ${current.attempt || 0}`));
    if (current.reason) context.append(element("p", "", current.reason));
    if (current.output) context.append(element("p", "", `Entregable registrado: ${current.output}`));
    if (current.approved_by) context.append(element("p", "", `Aceptación registrada: ${current.approved_by}`));
    wrapper.append(context);
  }
  const body = element("div", "detail-body");
  const actions = element("div");
  actions.append(element("p", "subheading", "QUÉ COMANDO EJECUTAR"), commandButton(stage.command));
  const list = element("ol", "action-list");
  stage.actions.forEach(action => list.append(element("li", "", action)));
  actions.append(list);
  const related = element("div", "command-list");
  stage.related.forEach(command => related.append(commandButton(command)));
  actions.append(related);
  const evidence = element("div");
  evidence.append(element("p", "subheading", "DÓNDE VER LA EVIDENCIA"));
  const prefix = project ? project.folder : "proyectos/<id>";
  stage.evidence.forEach(path => evidence.append(element("code", "path", `${prefix}/${path}`)));
  evidence.append(element("p", "subheading", "QUÉ DEBE QUEDAR LISTO"));
  const outputs = element("ul");
  stage.outputs.forEach(output => outputs.append(element("li", "", output)));
  evidence.append(outputs);
  body.append(actions, evidence);
  wrapper.append(body, element("div", "gate", stage.gate));
  return wrapper;
}
function renderManual(id) {
  const selected = stages.find(stage => stage.id === id) || stages[0];
  const flow = byId("flow");
  flow.replaceChildren();
  stages.forEach(stage => {
    const button = element("button", `step${stage.id === selected.id ? " selected" : ""}`);
    button.type = "button";
    button.setAttribute("aria-pressed", String(stage.id === selected.id));
    const top = element("div", "step-top");
    top.append(element("span", "", stage.number), element("span", "step-arrow", "↗"));
    button.append(top, element("h3", "", stage.title), element("p", "", stage.summary));
    button.addEventListener("click", () => {location.hash = `manual/${stage.id}`;});
    flow.append(button);
  });
  byId("stage-detail").replaceChildren(stageDetail(selected));
  // Avoid duplicate .detail borders when inserting the detail into its fixed slot.
  byId("stage-detail").classList.remove("detail");
}
function projectState(project) {
  if (project.health === "error") return ["error", "Estado no legible"];
  if (project.health !== "ok") return ["pendiente", "Sin inicializar"];
  if (!project.next_step) return ["completado", "Flujo completado"];
  const current = project.steps[project.next_step].status;
  return [current, labels[current]];
}
function renderProjects(projectId, stageId) {
  const grid = byId("projects-grid");
  grid.replaceChildren();
  if (!projects.length) grid.append(element("div", "empty", "No hay carpetas de proyectos. En tu chat, escribe !nuevo <id> para crear el primer expediente."));
  projects.forEach(project => {
    const button = element("button", `project-card${project.id === projectId ? " selected" : ""}`);
    button.type = "button";
    const top = element("div", "project-top");
    const [status, label] = projectState(project);
    top.append(element("h3", "", project.id), statusBadge(status, label));
    button.append(top, element("code", "quiet", `${project.folder}/`));
    const next = stages.find(s => s.id === project.next_step);
    button.append(element("p", "", project.health === "ok" ? (next ? `Próxima etapa: ${next.title}` : "Todas las etapas están completadas u omitidas.") : project.message));
    const progress = element("progress", "bar");
    progress.max = 100; progress.value = project.progress;
    progress.setAttribute("aria-label", `Avance de ${project.id}`);
    button.append(progress);
    const meta = element("div", "project-meta");
    meta.append(element("span", "", `${project.completed}/7 etapas`), element("span", "", `${project.progress}%`));
    button.append(meta);
    button.addEventListener("click", () => {location.hash = `proyectos/${encodeURIComponent(project.id)}`;});
    grid.append(button);
  });
  const detail = byId("project-detail");
  detail.replaceChildren();
  if (!projectId) return;
  const project = projects.find(p => p.id === projectId);
  if (!project) {detail.append(element("p", "empty", "La carpeta seleccionada ya no está disponible.")); return;}
  detail.append(element("h2", "project-detail-title", `Flujo de ${project.id}`));
  if (project.health !== "ok") {detail.append(element("p", "empty", project.message)); return;}
  const selected = stages.find(s => s.id === stageId) || stages.find(s => s.id === project.next_step) || stages.at(-1);
  const flow = element("div", "project-flow");
  stages.forEach(stage => {
    const button = element("button", stage.id === selected.id ? "selected" : "");
    button.type = "button";
    button.setAttribute("aria-pressed", String(stage.id === selected.id));
    button.append(element("span", "", `${stage.number} · ${stage.title}`), statusBadge(project.steps[stage.id].status));
    button.addEventListener("click", () => {location.hash = `proyectos/${encodeURIComponent(project.id)}/${stage.id}`;});
    flow.append(button);
  });
  detail.append(flow, stageDetail(selected, project));
  const activity = element("section", "activity");
  activity.append(element("h3", "", "Actividad reciente"));
  const list = element("ul");
  [...project.events].reverse().forEach(event => {
    const row = element("li");
    row.append(element("time", "", formatDate(event.at)), element("span", "", event.message));
    list.append(row);
  });
  if (!project.events.length) list.append(element("li", "", "No hay actividad registrada."));
  activity.append(list);
  detail.append(activity, element("p", "quiet", "El porcentaje cuenta etapas completadas u omitidas; no representa esfuerzo consumido. Las rutas indican dónde encontrar la evidencia local."));
}
function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value || "Sin fecha") : date.toLocaleString("es-CO");
}
function render() {
  if (!stages.length) return;
  const [page, id, stage] = route();
  const isProjects = page === "proyectos";
  byId("manual-view").hidden = isProjects;
  byId("projects-view").hidden = !isProjects;
  byId("nav-manual").classList.toggle("active", !isProjects);
  byId("nav-projects").classList.toggle("active", isProjects);
  byId("breadcrumb").textContent = isProjects ? "Expedientes / seguimiento del flujo" : "Guía de operación / manual del flujo";
  byId("project-count").textContent = projects.length;
  if (isProjects) renderProjects(id, stage); else renderManual(id);
}
async function refreshProjects() {
  if (refreshing) return;
  refreshing = true;
  try {
    const response = await fetch("/api/projects", {cache: "no-store"});
    if (!response.ok) throw new Error("No se pudo consultar el estado local.");
    const data = await response.json();
    if (!Array.isArray(data.projects)) throw new Error("Reinicia el portal con python scripts/framework.py serve.");
    const signature = JSON.stringify(data.projects);
    projects = data.projects;
    if (signature !== previousProjects) {previousProjects = signature; render();}
    byId("refresh-time").textContent = `Consulta: ${new Date().toLocaleTimeString("es-CO")}`;
    showNotice("");
  } catch (error) {
    showNotice(`No se pudo actualizar: ${error.message} Inicia el servidor desde la raíz con python scripts/framework.py serve.`);
  } finally {refreshing = false;}
}
window.addEventListener("hashchange", render);
byId("refresh").addEventListener("click", refreshProjects);
(async () => {
  try {
    const response = await fetch("/flujo.json", {cache: "no-store"});
    if (!response.ok) throw new Error("No se encontró el manual.");
    stages = (await response.json()).stages;
    render();
    await refreshProjects();
    setInterval(refreshProjects, 10000);
  } catch (error) {showNotice(`No se pudo abrir el manual: ${error.message}`);}
})();
