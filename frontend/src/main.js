import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "./App.vue"
import router from "./router"

import { Button, Badge, FormControl, setConfig, frappeRequest, resourcesPlugin } from "frappe-ui"

import { session } from "@/data/session"
import { userResource } from "@/data/user"
import { employeeResource } from "@/data/employee"
import dayjs from "@/utils/dayjs"

import "./index.css"

const app = createApp(App)
const pinia = createPinia()

setConfig("resourceFetcher", frappeRequest)
app.use(resourcesPlugin)
app.use(pinia)
app.use(router)

app.component("Button", Button)
app.component("Badge", Badge)
app.component("FormControl", FormControl)

if (session.isLoggedIn) {
  userResource.fetch()
  employeeResource.fetch()
}

app.provide("$session", session)
app.provide("$user", userResource)
app.provide("$employee", employeeResource)
app.provide("$dayjs", dayjs)

app.mount("#app")
