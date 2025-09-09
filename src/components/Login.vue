<template>
  <div style="padding: 2rem;">
    <h1>Fuwamofu Mail</h1>
    <div v-if="!isLoggedIn" id="g_id_signin" style="margin-top: 1rem;"></div>
    <div v-else>
      <h2>Welcome, {{ userEmail }}</h2>
      <button @click="loadGmailMessages">Load My Inbox</button>
      <div id="inbox-container" style="margin-top: 1rem; border-top: 1px solid #ccc; padding-top: 1rem;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isLoggedIn = ref(false)
const userEmail = ref('')
const accessToken = ref('')

onMounted(() => {
  const waitForGoogle = setInterval(() => {
    if (window.google && window.google.accounts && window.google.accounts.id) {
      clearInterval(waitForGoogle)

      window.google.accounts.id.initialize({
        client_id: '343822659955-sjqmuqskg0s15buvhfm8ndj0u0p6hcba.apps.googleusercontent.com',
        callback: handleCredentialResponse,
        auto_select: false,
        context: 'signin'
      })

      window.google.accounts.id.prompt()
    }
  }, 100)
})

function handleCredentialResponse(response) {
  // Use the ID token to get the access token and user info
  window.google.accounts.oauth2.initTokenClient({
    client_id: '343822659955-sjqmuqskg0s15buvhfm8ndj0u0p6hcba.apps.googleusercontent.com',
    scope: 'https://www.googleapis.com/auth/gmail.readonly',
    callback: (tokenResponse) => {
      accessToken.value = tokenResponse.access_token
      isLoggedIn.value = true
      userEmail.value = JSON.parse(atob(response.credential.split('.')[1])).email
    },
  }).requestAccessToken()
}

async function loadGmailMessages() {
  const inboxContainer = document.getElementById('inbox-container')
  if (!accessToken.value) {
    inboxContainer.innerHTML = '<p style="color:red;">Error: Access token not available.</p>'
    return
  }

  inboxContainer.innerHTML = '<p>Loading messages...</p>'
  
  try {
    const response = await fetch('https://www.googleapis.com/gmail/v1/users/me/messages?maxResults=10', {
      headers: {
        'Authorization': `Bearer ${accessToken.value}`
      }
    })

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`)
    }

    const data = await response.json()
    inboxContainer.innerHTML = '<h3>Latest Emails</h3>'
    
    if (data.messages && data.messages.length > 0) {
      data.messages.forEach(async (message) => {
        const messageResponse = await fetch(`https://www.googleapis.com/gmail/v1/users/me/messages/${message.id}?format=metadata&metadataHeaders=From,Subject,Date`, {
          headers: {
            'Authorization': `Bearer ${accessToken.value}`
          }
        })
        const messageData = await messageResponse.json()
        const from = messageData.payload.headers.find(h => h.name === 'From').value
        const subject = messageData.payload.headers.find(h => h.name === 'Subject').value
        const date = messageData.payload.headers.find(h => h.name === 'Date').value
        
        const messageElement = document.createElement('div')
        messageElement.innerHTML = `<div style="border: 1px solid #eee; padding: 0.5rem; margin-bottom: 0.5rem;"><strong>From:</strong> ${from}<br/><strong>Subject:</strong> ${subject}<br/><strong>Date:</strong> ${date}</div>`
        inboxContainer.appendChild(messageElement)
      })
    } else {
      inboxContainer.innerHTML += '<p>No messages found in your inbox.</p>'
    }
  } catch (error) {
    inboxContainer.innerHTML = `<p style="color:red;">Failed to load inbox: ${error.message}</p>`
    console.error(error)
  }
}
</script>