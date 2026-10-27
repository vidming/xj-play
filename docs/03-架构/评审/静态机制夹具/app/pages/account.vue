<script setup>
const message = ref('AV1_PRIVATE_SHELL')
onMounted(async () => {
  try {
    const response = await fetch('/__av1_private')
    if (!response.ok) throw new Error('Unauthenticated fixture')
    const payload = await response.json()
    message.value = payload.message
  } catch { message.value = 'AV1_PRIVATE_SHELL' }
})
</script>
<template><main><h1>Account</h1><p>{{ message }}</p></main></template>
