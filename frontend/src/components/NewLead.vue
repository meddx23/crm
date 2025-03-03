<template>
  <div class="flex flex-col gap-4">
    <div v-for="section in allFields" :key="section.section">
      <div class="grid grid-cols-3 gap-4">
        <div v-for="field in section.fields" :key="field.name">
          <div class="mb-2 text-sm text-gray-600">{{ field.label }}</div>
          <FormControl
            v-if="field.type === 'select'"
            type="select"
            :options="field.options"
            v-model="newLead[field.name]"
          >
            <template v-if="field.name == 'status'" #prefix>
              <IndicatorIcon :class="getLeadStatus(newLead[field.name]).iconColorClass" />
            </template>
          </FormControl>
          <FormControl
            v-else-if="field.type === 'email'"
            type="email"
            v-model="newLead[field.name]"
          />
          <Link
            v-else-if="field.type === 'link'"
            class="form-control"
            :value="newLead[field.name]"
            :doctype="field.doctype"
            @change="(e) => field.change(e)"
            :placeholder="field.placeholder"
            :onCreate="field.create"
          />
          <FormControl
            v-else-if="field.type === 'user'"
            type="autocomplete"
            :options="activeAgents"
            :value="getUser(newLead[field.name]).full_name"
            @change="(option) => (newLead[field.name] = option.email)"
            :placeholder="field.placeholder"
          >
            <template #prefix>
              <UserAvatar class="mr-2" :user="newLead[field.name]" size="sm" />
            </template>
            <template #item-prefix="{ option }">
              <UserAvatar class="mr-2" :user="option.email" size="sm" />
            </template>
          </FormControl>
          <FormControl v-else type="text" v-model="newLead[field.name]" />
        </div>
      </div>
    </div>
  </div>
  <OrganizationModal
    v-model="showOrganizationModal"
    :organization="_organization"
    :options="{
      redirect: false,
      afterInsert: (doc) => (newLead.organization = doc.name),
    }"
  />
</template>

<script setup>
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import OrganizationModal from '@/components/Modals/OrganizationModal.vue'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { activeAgents } from '@/utils'
import { FormControl, Button, Dropdown, FeatherIcon } from 'frappe-ui'
import { ref } from 'vue'

const { getUser } = usersStore()
const { getLeadStatus, statusOptions } = statusesStore()

const props = defineProps({
  newLead: {
    type: Object,
    required: true,
  },
})

const showOrganizationModal = ref(false)
const _organization = ref({})

const allFields = [
  {
    section: 'Lead Details',
    fields: [
      {
        label: 'Salutation',
        name: 'salutation',
        type: 'select',
        options: [
          {
            label: 'Mr',
            value: 'Mr',
          },
          {
            label: 'Ms',
            value: 'Ms',
          },
          {
            label: 'Mrs',
            value: 'Mrs',
          },
        ],
      },
      {
        label: 'First Name',
        name: 'first_name',
        type: 'data',
      },
      {
        label: 'Last Name',
        name: 'last_name',
        type: 'data',
      },
      {
        label: 'Email',
        name: 'email',
        type: 'data',
      },
      {
        label: 'Mobile No',
        name: 'mobile_no',
        type: 'data',
      },
    ],
  },
  {
    section: 'Other Details',
    fields: [
      {
        label: 'Organization',
        name: 'organization',
        type: 'link',
        placeholder: 'Organization',
        doctype: 'CRM Organization',
        change: (data) => (props.newLead.organization = data),
        create: (value, close) => {
          _organization.value.organization_name = value
          showOrganizationModal.value = true
          close()
        },
      },
      {
        label: 'Status',
        name: 'status',
        type: 'select',
        options: statusOptions('lead'),
      },
      {
        label: 'Lead Owner',
        name: 'lead_owner',
        type: 'user',
        placeholder: 'Lead Owner',
      },
    ],
  },
]
</script>
