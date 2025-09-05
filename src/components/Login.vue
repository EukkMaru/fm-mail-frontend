<script setup>
import { ref, onMounted } from 'vue'

const userEmail = ref('')

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

      window.google.accounts.id.renderButton(
        document.getElementById("g_id_signin"),
        { theme: "outline", size: "large" }
      )
    }
  }, 100)
})


function handleCredentialResponse(response) {
  const token = response.credential
  console.log("ID Token:", token)
  // You can decode this token if needed using jwt.io or your backend
}
</script>

<template>
  <div>
    <div id="g_id_signin"></div>
  </div>
</template>
