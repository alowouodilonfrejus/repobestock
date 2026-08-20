<template>
  <NuxtLayout name="dashboard">
    <div class="max-w-6xl mx-auto">
      <div class="mb-10 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">Gestion des utilisateurs</h2>
          <p class="text-gray-500 mt-2 text-base sm:text-lg">Créez, modifiez et contrôlez les comptes de la plateforme.</p>
        </div>
        <button
          @click="openCreate"
          class="px-6 py-3 bg-blue-900 text-white rounded-lg text-sm font-semibold hover:bg-blue-800 transition shadow-sm flex-shrink-0 w-full sm:w-auto"
        >
          + Nouvel utilisateur
        </button>
      </div>

      <UiCard class="shadow-sm border border-gray-200 overflow-hidden p-0">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50 text-gray-500 uppercase text-xs">
              <tr>
                <th class="px-6 py-4 font-semibold">Utilisateur</th>
                <th class="px-6 py-4 font-semibold">Rôle</th>
                <th class="px-6 py-4 font-semibold">Statut</th>
                <th class="px-6 py-4 font-semibold">Créé le</th>
                <th class="px-6 py-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="user in sortedUsers" :key="user.id" class="hover:bg-gray-50">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-blue-900 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {{ initials(user) }}
                    </div>
                    <div>
                      <p class="font-semibold text-gray-900">{{ user.username || user.email }}</p>
                      <p class="text-gray-500 text-xs">{{ user.email }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span class="text-xs font-semibold px-2.5 py-1 rounded-full" :class="roleBadge(user.role)">
                    {{ roleLabel(user.role) }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span
                    class="text-xs font-semibold px-2.5 py-1 rounded-full"
                    :class="user.is_active ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'"
                  >
                    {{ user.is_active ? 'Actif' : 'En attente' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-gray-500">{{ formatDate(user.created_at) }}</td>
                <td class="px-6 py-4 text-right whitespace-nowrap">
                  <button
                    v-if="!user.is_active"
                    @click="openApprove(user)"
                    :disabled="user.id === currentUserId"
                    class="text-green-700 hover:bg-green-50 px-3 py-1.5 rounded-lg font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    Activer
                  </button>
                  <button
                    @click="openEdit(user)"
                    :disabled="user.id === currentUserId"
                    class="text-blue-700 hover:bg-blue-50 px-3 py-1.5 rounded-lg font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    Modifier
                  </button>
                  <button
                    @click="confirmDelete(user)"
                    :disabled="user.id === currentUserId"
                    class="text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-lg font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
              <tr v-if="store.loading">
                <td colspan="5" class="px-6 py-10 text-center text-gray-400">Chargement...</td>
              </tr>
              <tr v-else-if="sortedUsers.length === 0">
                <td colspan="5" class="px-6 py-10 text-center text-gray-400">Aucun utilisateur.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UiCard>

      <div v-if="showApprove" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="closeApprove">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Valider l'inscription</h3>
          <p class="text-gray-500 mb-6">
            Confirmer le compte <span class="font-semibold text-gray-800">{{ approveUser?.email }}</span> et lui attribuer son rôle.
          </p>

          <form @submit.prevent="handleApprove" class="space-y-2">
            <UiSelect label="Rôle à attribuer" v-model="approveRole">
              <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
            </UiSelect>

            <div class="flex justify-end gap-4 pt-6">
              <button type="button" @click="closeApprove" class="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-100 transition">
                Annuler
              </button>
              <button type="submit" class="px-6 py-2.5 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700 transition">
                Valider
              </button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="closeModal">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-6">
            {{ editing ? 'Modifier l\'utilisateur' : 'Nouvel utilisateur' }}
          </h3>

          <form @submit.prevent="handleSubmit" class="space-y-2">
            <UiInput label="Nom d'utilisateur" type="text" v-model="form.username" placeholder="ex: johndoe" />
            <UiInput label="Email" type="email" v-model="form.email" placeholder="ex: john@example.com" :disabled="!!editing" />
            <UiInput
              v-if="!editing || form.password"
              label="Mot de passe"
              type="password"
              v-model="form.password"
              :placeholder="editing ? 'Laisser vide pour ne pas changer' : 'Mot de passe'"
            />
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <UiSelect label="Rôle" v-model="form.role">
                <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
              </UiSelect>
              <UiSelect v-if="editing" label="Statut" v-model="form.is_active">
                <option :value="true">Actif</option>
                <option :value="false">Inactif</option>
              </UiSelect>
            </div>

            <div class="flex flex-wrap justify-end gap-4 pt-6">
              <button type="button" @click="closeModal" class="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-100 transition w-full sm:w-auto">
                Annuler
              </button>
              <button type="submit" class="px-6 py-2.5 bg-blue-900 text-white rounded-lg text-sm font-semibold hover:bg-blue-800 transition w-full sm:w-auto">
                {{ editing ? 'Enregistrer' : 'Créer' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue';
import { useAuthStore } from '~/stores/auth';
import { useUsersStore } from '~/stores/users';
import { getErrorMessage } from '@/utils/errors';

const store = useUsersStore();
const authStore = useAuthStore();
const toast = useToast();
const { confirmDialog } = useConfirm();

const sortedUsers = computed(() => {
  return [...store.users].sort((a, b) => Number(a.is_active) - Number(b.is_active));
});

const roles = [
  { value: 'superadmin', label: 'Super Admin' },
  { value: 'admin', label: 'Admin' },
  { value: 'manager', label: 'Manager' },
];

const showModal = ref(false);
const editing = ref(null);
const showApprove = ref(false);
const approveUser = ref(null);
const approveRole = ref('manager');
const form = reactive({ email: '', username: '', password: '', role: 'manager', is_active: true });

const currentUserId = authStore.user?.id;

const roleLabel = (role) => roles.find((r) => r.value === role)?.label || role;
const roleBadge = (role) => ({
  superadmin: 'bg-purple-50 text-purple-700',
  admin: 'bg-blue-50 text-blue-700',
  manager: 'bg-amber-50 text-amber-700',
}[role] || 'bg-gray-100 text-gray-600');

const initials = (user) => {
  const name = user.username || user.email || '?';
  return name.split(/[.\s@]/).filter(Boolean).slice(0, 2).map((p) => p[0]).join('').toUpperCase();
};

const formatDate = (date) => {
  if (!date) return '—';
  return new Date(date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
};

const openCreate = () => {
  editing.value = null;
  Object.assign(form, { email: '', username: '', password: '', role: 'manager', is_active: true });
  showModal.value = true;
};

const openEdit = (user) => {
  editing.value = user;
  Object.assign(form, { email: user.email, username: user.username, password: '', role: user.role, is_active: user.is_active });
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  editing.value = null;
};

const openApprove = (user) => {
  approveUser.value = user;
  approveRole.value = user.role;
  showApprove.value = true;
};

const closeApprove = () => {
  showApprove.value = false;
  approveUser.value = null;
};

const handleApprove = async () => {
  try {
    await store.updateUser(approveUser.value.id, { is_active: true, role: approveRole.value });
    toast.success('Compte activé avec succès.');
    closeApprove();
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
};

const handleSubmit = async () => {
  try {
    if (editing.value) {
      const payload = { username: form.username, role: form.role, is_active: form.is_active };
      if (form.password) payload.password = form.password;
      await store.updateUser(editing.value.id, payload);
      toast.success('Utilisateur modifié avec succès.');
    } else {
      if (!form.email.trim() || !form.password) {
        toast.error('Email et mot de passe sont obligatoires.');
        return;
      }
      await store.createUser({ email: form.email, username: form.username, password: form.password, role: form.role });
      toast.success('Utilisateur créé avec succès.');
    }
    closeModal();
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
};

const confirmDelete = async (user) => {
  const ok = await confirmDialog({
    title: 'Supprimer l\'utilisateur',
    message: `Supprimer ${user.username || user.email} ? Cette action est irréversible.`,
    confirmLabel: 'Supprimer',
    danger: true,
  });
  if (!ok) return;
  try {
    await store.deleteUser(user.id);
    toast.success('Utilisateur supprimé.');
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
};

onMounted(() => {
  store.fetchUsers();
});
</script>