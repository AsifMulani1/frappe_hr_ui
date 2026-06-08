import dayjs from "dayjs"
import updateLocale from "dayjs/plugin/updateLocale"
import relativeTime from "dayjs/plugin/relativeTime"
import localizedFormat from "dayjs/plugin/localizedFormat"
import isToday from "dayjs/plugin/isToday"

dayjs.extend(updateLocale)
dayjs.extend(relativeTime)
dayjs.extend(localizedFormat)
dayjs.extend(isToday)

export default dayjs
