<script>
  import { onMount } from "svelte";
  

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  let apimessage = [];

  onMount(async () => {
    let resp = await fetch("/api/checkservers").then((res) => res.json());
    console.log(resp);
  apimessage = resp;
  });

  async function doPost(id, type) {
    const res = await fetch("/api/checkservers", {
      method: 'POST',
      body: JSON.stringify({
        'guildinfo':id,
        'setting_type':type,
      }),
      headers: {
        "Content-Type": "application/json",
        'X-CSRFToken': csrftoken,
      },
      mode: 'same-origin',
    })
  }
</script>

<header>
  <h1>DIRUPL</h1>
</header>

<main>
  <div class = "cards-container">
		{#each apimessage as guildinfo}
			<div class="flip-card">
				<div class="flip-card-inner">
					<div class="flip-card-front">
            <h3>Guild: {guildinfo.name}</h3>
            <h4>Server: {guildinfo.server.name}</h4>
						<p>{guildinfo.server.desc}</p>
					</div>
					<div class="flip-card-back">
            <div class="row">
              <div class="text-box">
                <p>Show events location</p>
              </div>
              <label class="switch">
                <input type="checkbox" checked={guildinfo.notification_settings.event_show_location} on:click={() => doPost(guildinfo.id, 'esl')}>
                <span class="slider round"></span>
              </label>
            </div>
            <div class="row">
              <div class="text-box">
                <p>Show distance to events</p>
              </div>
              <label class="switch">
                <input type="checkbox" checked={guildinfo.notification_settings.event_show_distance} on:click={() => doPost(guildinfo.id, 'esd')}>
                <span class="slider round"></span>
              </label>
            </div>
            <div class="row">
              <div class="text-box">
                <p>Show vending machines location</p>
              </div>
              <label class="switch">
                <input type="checkbox" checked={guildinfo.notification_settings.vend_show_location} on:click={() => doPost(guildinfo.id, 'vsl')}>
                <span class="slider round"></span>
              </label>
            </div>
            <div class="row">
              <div class="text-box">
                <p>Show distance to vending machines</p>
              </div>
              <label class="switch">
                <input type="checkbox" checked={guildinfo.notification_settings.vend_show_distance} on:click={() => doPost(guildinfo.id, 'vsd')}>
                <span class="slider round"></span>
              </label>
            </div>
					</div>
				</div>
		  	</div>
		{/each}
  </div>
</main>

<style>
* {
	padding: 0;
	margin: 0;
}

header {
    background-color: black;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 15vh;
    box-shadow: 5px 5px 10px rgb(0,0,0,0.3);
}

main {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
    background: url(https://wallpaperaccess.com/full/2002264.png);
    background-size: cover;
}

h1 {
    letter-spacing: 1.5vw;
    font-family: 'system-ui';
    text-transform: uppercase;
    text-align: center;
}
h3, h4 {
  margin-top: 10px;
  margin-bottom: 10px;
  font-family: "Bebas Neue",sans-serif;
  font-weight: 500;
  color: #e4dad1;
}

p {
	font-size: 14px;
	font-family: "Bebas Neue",sans-serif;
  font-weight: 500;
  color: #e4dad1;
  margin: 0; /* overrides the browser default-margin */
  padding: 0; /* overrides the browser default-padding */
}


.cards-container {
  display: flex;
  flex-wrap: wrap;
  margin: 0;
  min-height: 100%;
  height: 100%;
  width: 90%;
}
/* The flip card container - set the width and height to whatever you want. We have added the border property to demonstrate that the flip itself goes out of the box on hover (remove perspective if you don't want the 3D effect */
.flip-card {
  background-color: transparent;
  width: 300px;
  height: 300px;
  margin-left: 20px;
  margin-right: 20px;
  margin-top: 20px;
  margin-bottom: 20px;
  perspective: 1000px; /* Remove this if you don't want the 3D effect */
}

/* This container is needed to position the front and back side */
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.8s;
  transform-style: preserve-3d;
}

/* Do an horizontal flip when you move the mouse over the flip box container */
.flip-card:hover .flip-card-inner {
  transform: rotateY(180deg);
}

/* Position the front and back side */
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  padding: 0 10px;
  -webkit-backface-visibility: hidden; /* Safari */
  backface-visibility: hidden;
}

/* Style the front side (fallback if image is missing) */
.flip-card-front {
  background-color: #1e2020;
  color: black;
}

/* Style the back side */
.flip-card-back {
  background-color: #ce422b;
  color: white;
  transform: rotateY(180deg);
}

.row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  margin-left: 20px;
  margin-right: 20px;
  margin-top: 10px;
  margin-bottom: 10px;
}

.text-box {
  display: flex;
  text-align: left;
  width: 160px;
}
/* The switch - the box around the slider */
.switch {
  position: relative;
  display: inline-block;
  width: 52px;
  height: 30px;
  margin-left: 20px;
}

/* Hide default HTML checkbox */
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* The slider */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color:#f6eae0;
  -webkit-transition: .4s;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .slider {
  background-color: #2196F3;
}

input:focus + .slider {
  box-shadow: 0 0 1px #2196F3;
}

input:checked + .slider:before {
  -webkit-transform: translateX(22px);
  -ms-transform: translateX(22px);
  transform: translateX(22px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 30px;
}

.slider.round:before {
  border-radius: 50%;
}

</style>