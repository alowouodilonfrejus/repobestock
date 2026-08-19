<script setup lang="ts">

import odilon from '../../images/odilon.jpg'
import larick from '../../images/larick.jpg'
import naim from '../../images/naim.jpg'



interface Membre {
  id: number
  nom: string
  role: string
  photo: string
}

const equipe: Membre[] = [
  {
    id: 1,
    nom: 'ALOWOU Odilon',
    role: 'Développeur',
    photo: odilon,
  },
  {
    id: 2,
    nom: 'LOKOSSA Larick',
    role: 'Développeur',
    photo: larick,
  },
  {
    id: 3,
    nom: 'SABAM IMOROU ABDOUNAIM',
    role: 'Développeur',
    photo: naim,
  },
 
]
</script>

<template>
  <!-- Conteneur racine unique -->
  <div class="bg-[#23418e] min-h-screen flex flex-col justify-between font-sans">

    <!-- Section Équipe -->
    <section class="pt-12 pb-8 px-5">
      <div class="max-w-7xl mx-auto">

        <!-- En-tête de section -->
        <div class="text-center mb-8">
          <h2 class="text-4xl md:text-5xl font-extrabold text-white mb-3">
            L'Équipe <span class="text-[#f77b07]">BeStock</span>
          </h2>

          <div class="w-24 h-1.5 bg-[#f77b07] mx-auto rounded-full mb-4"></div>

          <p class="text-lg text-slate-200 max-w-2xl mx-auto">
            Découvrez les talents derrière la conception et le développement de votre plateforme de gestion de stock.
          </p>
        </div>

        <!-- Grille des membres -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <div
            v-for="dev in equipe"
            :key="dev.id"
            class="bg-white rounded-2xl p-6 shadow-xl text-center flex flex-col items-center transition-transform duration-300 hover:-translate-y-2"
          >
            <div class="relative w-36 h-36 mb-6">
              <img
                :src="dev.photo"
                :alt="dev.nom"
                class="w-full h-full object-cover rounded-full border-4 border-[#f77b07] shadow-md"
              />
            </div>

            <h3 class="text-2xl font-bold text-[#23418e] mb-1">
              {{ dev.nom }}
            </h3>

            <span class="inline-block bg-orange-100 text-[#f77b07] text-sm font-semibold px-3 py-1 rounded-full">
              {{ dev.role }}
            </span>
          </div>
        </div>

      </div>
    </section>

    <!-- Pied de page -->
    <footer class="w-full text-center text-xs text-slate-400 py-4">
      © {{ new Date().getFullYear() }}
      <span class="font-bold text-white">BESTOCK</span>.
      Tous droits réservés.
    </footer>

  </div>
</template>