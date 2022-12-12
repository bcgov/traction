<template>
  <div class="container">
    <div class="header">
      <div class="symbol">
        <svg
          class="w-6 h-6"
          data-darkreader-inline-stroke=""
          fill="none"
          stroke="currentColor"
          style="--darkreader-inline-stroke: currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
          ></path>
        </svg>
      </div>
      <div class="message">approved!</div>
    </div>
    <div class="content">content</div>
    <div class="footer">footer</div>
  </div>
</template>
<style scoped>
.container {
  display: grid;
  grid-template-rows: 100px 1fr 100px;
  grid-template-columns: 1fr;
  grid-template-areas:
    'header'
    'content'
    'footer';
  background-color: #d6deec;
  margin-top: 2rem;
  border-radius: 5px;
  border-style: solid;
  border-width: 4px;
  border-color: rgba(43, 54, 81, 0.1);
}
.header {
  grid-area: header;
  align-items: center;
  text-align: center;
  color: #2b3651;
  font-size: 1.6rem;
  font-weight: 800;
  padding: 1rem;
}
.header .message {
  text-transform: uppercase;
}
.header .symbol svg {
  stroke: #2b3651;
  height: 50px;
}
</style>
