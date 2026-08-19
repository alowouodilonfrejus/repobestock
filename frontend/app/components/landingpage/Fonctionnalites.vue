<script setup lang="ts">
const fonctionnalites = [
  {
    titre: 'Ajouter',
    description: "Permet d'ajouter de nouveaux équipements rapidement dans votre inventaire.",
    icon: 'heroicons:plus-circle'
  },
  {
    titre: 'Modifier',
    description: "Être capable de modifier les propriétés d'un équipement existant en modifiant certaines de ses caractéristiques.",
    icon: 'heroicons:pencil-square'
  },
  {
    titre: 'Supprimer',
    description: "Supprimer les équipements obsolètes ou hors service de votre base de données.",
    icon: 'heroicons:trash'
  }
]
</script>

<template>
  <div class="bg-[#23418e] px-8 pt-5 pb-6 font-sans">
    <div class="mx-auto max-w-7xl w-full text-center">

      <h1 class="text-4xl md:text-5xl font-extrabold text-slate-50 mb-12">
        Fonctionnalités
      </h1>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 justify-items-center">

        <section
          v-for="item in fonctionnalites"
          :key="item.titre"
          class="flex min-h-[200px] w-full flex-col items-center rounded-2xl bg-orange-50 p-6 text-center shadow-lg transition-transform duration-300 hover:-translate-y-1"
        >
          <div class="mb-4 flex items-center justify-center gap-2">
            <Icon
              :name="item.icon"
              class="h-8 w-8 text-orange-600"
            />

            <h2 class="text-2xl font-semibold text-orange-600">
              {{ item.titre }}
            </h2>
          </div>

          <p class="text-slate-700 leading-7">
            {{ item.description }}
          </p>

        </section>

      </div>

    </div>
  </div>
</template>