import { defineStore } from 'pinia'
import { createListResource } from 'frappe-ui'
import { reactive, h } from 'vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'

export const statusesStore = defineStore('crm-statuses', () => {
  let leadStatusesByName = reactive({})
  let dealStatusesByName = reactive({})

  const leadStatuses = createListResource({
    doctype: 'CRM Lead Status',
    fields: ['name', 'color', 'position'],
    orderBy: 'position asc',
    cache: 'lead-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.colorClass = colorClasses(status.color)
        status.iconColorClass = colorClasses(status.color, true)
        leadStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  const dealStatuses = createListResource({
    doctype: 'CRM Deal Status',
    fields: ['name', 'color', 'position'],
    orderBy: 'position asc',
    cache: 'deal-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.colorClass = colorClasses(status.color)
        status.iconColorClass = colorClasses(status.color, true)
        dealStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  function colorClasses(color, onlyIcon = false) {
    let textColor = `!text-${color}-600`
    if (color == 'black') {
      textColor = '!text-gray-900'
    } else if (['gray', 'green'].includes(color)) {
      textColor = `!text-${color}-700`
    }
  
    let bgColor = `!bg-${color}-100 hover:!bg-${color}-200 active:!bg-${color}-300`
  
    return [textColor, onlyIcon ? '' : bgColor]
  }

  function getLeadStatus(name) {
    return leadStatusesByName[name]
  }

  function getDealStatus(name) {
    return dealStatusesByName[name]
  }

  function statusOptions(doctype, action) {
    let statusesByName =
      doctype == 'deal' ? dealStatusesByName : leadStatusesByName
    let options = []
    for (const status in statusesByName) {
      options.push({
        label: statusesByName[status].name,
        icon: () =>
          h(IndicatorIcon, {
            class: statusesByName[status].iconColorClass,
          }),
        onClick: () => {
          action && action('status', statusesByName[status].name)
        },
      })
    }
    return options
  }

  return {
    leadStatuses,
    dealStatuses,
    getLeadStatus,
    getDealStatus,
    statusOptions,
  }
})
