import "./app.css";
import App from "./App.svelte";

const appTargetEl = document.getElementById("app");
if (!appTargetEl) throw Error("App DOM Element not found, cannot initialize.");
const app = new App({ target: appTargetEl });

export default app;
