<template >
  <div class="students">
    <v-parallax dark src="@/assets/images/library.jpg" class="faber-header">
      <v-row align="center" justify="center">
        <v-col class="text-center" cols="12">
          <h1 class="mb-4" color="red">Faber University</h1>
          <h4 class="subheading">Student Registry</h4>
        </v-col>
      </v-row>
    </v-parallax>
    <v-container>
      <Students />
    </v-container>
  </div>
</template>

<script>
import Students from '@/components/faber/Students.vue';
export default {
  name: 'Faber',
  components: {
    Students,
  },
};
</script>

<style lang="scss" scoped>
.students {
  height: 100%;
  font-family:'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif !important;
  background-color: rgb(218, 207, 198) !important;
}
.faber-header {
  h1, h4 {
    background-color: rgba(218, 207, 198, 0.4);
    padding: 2px;
    padding: 2px;
  }
  h1 {
    font-size: 7em;
  }
  h4 {
    font-size: 2em;
  }
}
</style>
