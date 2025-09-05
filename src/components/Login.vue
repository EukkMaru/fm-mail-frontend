<script setup>
import { onMounted } from 'vue'
import { gapi } from 'gapi-script'

const clientId = '343822659955-sjqmuqskg0s15buvhfm8ndj0u0p6hcba.apps.googleusercontent.com'
const scopes = 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send'

function start() {
  gapi.client.init({
    clientId,
    scope: scopes,
  })
}

function handleLogin() {
  gapi.load('client:auth2', () => {
    gapi.auth2.init({ client_id: clientId }).then(() => {
      const authInstance = gapi.auth2.getAuthInstance()
      authInstance.signIn().then(user => {
        const token = user.getAuthResponse().access_token
        console.log('Access Token:', token)
        // TODO: Use this token to call Gmail API
      })
    })
  })
}

onMounted(() => {
  gapi.load('client:auth2', start)
})
</script>

<template>
  <button @click="handleLogin">Login</button>
</template>
