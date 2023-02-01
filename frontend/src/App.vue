<template>
  <div id="app">
    <div>
      connection: {{ connection ? 'online' : 'offline' }}
    </div>
    <div>
      device id: <input type="number" v-model="deviceId"/>
    </div>
    <div class="frame">
      <img :src="image" @load="onImgLoad"/>
    </div>
  </div>
</template>

<style>
  .frame {
    margin-top: 1ch;
    display: block;
    border-radius: 6px;
    width: 640px;
    height: 480px;
  }
  .frame img {
    max-height: 100%;
    max-width: 100%;
    height: auto;
    width: auto;
    border-radius: 6px;
  }
</style>

<script>
export default {
  name: "App",
  data: function () {
    return {
      connection: null,
      image: null,
      deviceId: 0,
      inputTimeout: 0,
      reconnectionInterval: 0,
      isConnecting: false,
    };
  },
  methods: {
    onImgLoad: function() {
      if (!this.image) {
        return;
      }
      URL.revokeObjectURL(this.image);
    },
    onWsMessage: function(event) {
      if (!event || !(event.data instanceof Blob)) {
        return;
      }
      this.image = URL.createObjectURL(event.data);
    },
    wsClose: function() {
      if (this.connection) {
        this.connection.close();
      }
    },
    wsReconnect: function() {
      if (this.isConnecting) {
        return;
      }
      this.isConnecting = true;
      this.wsClose();
      if (isNaN(Number(this.deviceId))) {
        return;
      }
      const connection = new WebSocket(`ws://${location.host}/ws/${this.deviceId}`);
      console.log('establishing connection', connection);

      connection.addEventListener(
        'open',
        () => {
          console.log('opened', connection);
          this.connection = connection;
          this.isConnecting = false;
        }
      );
      connection.addEventListener(
        'close',
        () => {
          console.log('closed', connection);
          this.connection = null;
          this.isConnecting = false;
        }
      )
      connection.addEventListener(
        'message',
        (event) => {
          this.onWsMessage(event);
        }
      )
    },
  },
  created: function () {
    this.wsReconnect();
  },
  watch: {
    deviceId: function() {
      if (this.inputTimeout) {
        clearTimeout(this.inputTimeout);
      }
      this.inputTimeout = setTimeout(
        () => {
          this.wsReconnect();
        },
        500,
      )
    },
    connection: function(connection) {
      if (connection) {
        clearInterval(this.reconnectionInterval);
        return;
      }
      this.reconnectionInterval = setInterval(
        () => {
          this.wsReconnect()
        },
        1000,
      )

    },
  }
};
</script>