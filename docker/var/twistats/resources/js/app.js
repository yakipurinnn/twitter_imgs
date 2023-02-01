import './bootstrap';


import { createApp } from "vue";
import App from "./App.vue";

const app = createApp(App);

console.log(app.version);

app.mount("#app");