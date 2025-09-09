<template>
  <div style="padding: 2rem;">
    <h1>Fuwamofu Mail</h1>
    <div v-if="!isLoggedIn">
      <button @click="login">Sign in with Google</button>
    </div>
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

const CLIENT_ID = '343822659955-ts35vt5d29gdkfmarbbjbat66tfha3id.apps.googleusercontent.com';
const REDIRECT_URI = 'https://mail.fuwamofu.net';

onMounted(() => {
  const fragment = window.location.hash.substring(1);
  const params = new URLSearchParams(fragment);
  const token = params.get('access_token');

  if (token) {
    accessToken.value = token;
    isLoggedIn.value = true;
    getUserEmail();
    
    // Clean up the URL
    window.history.replaceState({}, document.title, window.location.pathname);
  }
});

function login() {
  const oauth2Endpoint = 'https://accounts.google.com/o/oauth2/v2/auth';

  const params = {
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    response_type: 'token',
    scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email',
    include_granted_scopes: 'true',
    prompt: 'select_account consent',
    state: 'pass-through-value'
  };

  const url = `${oauth2Endpoint}?${new URLSearchParams(params)}`;
  window.location.href = url;
}

async function getUserEmail() {
  if (!accessToken.value) return;

  try {
    const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: {
        'Authorization': `Bearer ${accessToken.value}`
      }
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    const data = await response.json();
    userEmail.value = data.email;
  } catch (error) {
    console.error('Failed to get user email:', error);
  }
}

async function loadGmailMessages() {
  console.log('Starting loadGmailMessages');
  const inboxContainer = document.getElementById('inbox-container')
  if (!accessToken.value) {
    console.error('Access token not available.');
    inboxContainer.innerHTML = '<p style="color:red;">Error: Access token not available.</p>'
    return
  }
  console.log('Access Token:', accessToken.value);

  inboxContainer.innerHTML = '<p>Loading messages...</p>'
  
  try {
    console.log('Fetching message list...');
    const response = await fetch('https://www.googleapis.com/gmail/v1/users/me/messages?maxResults=10', {
      headers: {
        'Authorization': `Bearer ${accessToken.value}`
      }
    })

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`)
    }

    const data = await response.json()
    console.log('Message list response:', data);
    inboxContainer.innerHTML = '<h3>Latest Emails</h3>'
    
    if (data.messages && data.messages.length > 0) {
      console.log('Message IDs found:', data.messages.map(m => m.id));
      const messagePromises = data.messages.map(message => {
        console.log('Fetching message ID:', message.id);
        return fetch(`https://www.googleapis.com/gmail/v1/users/me/messages/${message.id}?format=metadata&metadataHeaders=From,Subject,Date`, {
          headers: {
            'Authorization': `Bearer ${accessToken.value}`
          }
        }).then(res => res.json())
      });

      try {
        console.log('Waiting for all message promises to resolve...');
        const messages = await Promise.all(messagePromises);
        console.log('All messages fetched:', messages);

        messages.forEach(messageData => {
          console.log('Processing message data:', messageData);
          if (messageData.payload && messageData.payload.headers) {
            const from = messageData.payload.headers.find(h => h.name === 'From')?.value || 'N/A'
            const subject = messageData.payload.headers.find(h => h.name === 'Subject')?.value || 'N/A'
            const date = messageData.payload.headers.find(h => h.name === 'Date')?.value || 'N/A'
            
            const messageElement = document.createElement('div')
            messageElement.innerHTML = `<div style=\"border: 1px solid #eee; padding: 0.5rem; margin-bottom: 0.5rem;\"><strong>From:</strong> ${from}<br/><strong>Subject:</strong> ${subject}<br/><strong>Date:</strong> ${date}</div>`
            inboxContainer.appendChild(messageElement)
          } else {
            console.warn('Message data has no payload or headers:', messageData);
          }
        });
      } catch (error) {
        console.error('Error fetching individual messages:', error);
        inboxContainer.innerHTML += '<p style=\"color:red;\">Error fetching some emails.</p>';
      }

    } else {
      console.log('No messages found in inbox.');
      inboxContainer.innerHTML += '<p>No messages found in your inbox.</p>'
    }
  } catch (error) {
    console.error('Failed to load inbox:', error);
    inboxContainer.innerHTML = `<p style="color:red;">Failed to load inbox: ${error.message}</p>`
  }
}
</script>
