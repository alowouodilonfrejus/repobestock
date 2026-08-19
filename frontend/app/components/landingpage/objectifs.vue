<script setup lang="ts">
const titre = "Objectifs"
</script>

<template>
  <main class="min-h-screen flex justify-center items-center bg-[#23418e] p-10 font-sans">
    <section class="w-full max-w-[950px] text-center">
      <h1 class="text-[42px] text-white mb-[15px] font-bold">
        {{ titre }}
      </h1>

      <div class="w-[90px] h-[5px] bg-white mx-auto mb-[35px] rounded-[20px]"></div>

      <div class="text-[19px] text-white leading-[2] text-justify space-y-6">
        <p>
          <strong class="text-[#f77b07] font-bold">BeStock</strong> est une solution numérique innovante développée
          par <strong class="text-[#f77b07] font-bold">BeTogether</strong>, le premier espace où les marques, de toutes tailles et de tous horizons, sont mises en valeur, fidélisent leur clientèle, créent des liens avec des utilisateurs du monde entier et atteignent leurs objectifs commerciaux.
        </p>
        <p>
          Notre ambition est d'offrir une solution moderne, intuitive et
          performante permettant à l'entreprise de gérer efficacement son
          stock, de suivre les mouvements des matériaux en temps réel et
          d'automatiser les opérations de gestion .
        </p>
        <p>
          BeStock facilite également la prise de décision grâce à des rapports
          détaillés, des statistiques fiables et des indicateurs de performance.
          La sécurité des données, la simplicité d'utilisation et l'amélioration
          continue de l'expérience utilisateur constituent les principales
          priorités de la plateforme.
        </p>
      </div>
    </section>
  </main>
</template>