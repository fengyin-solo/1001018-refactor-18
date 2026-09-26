import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '@/views/Dashboard.vue'
const Facility = () => import('@/views/facility/index.vue')
const Bridge = () => import('@/views/bridge/index.vue')
const Tunnel = () => import('@/views/tunnel/index.vue')
const Pavement = () => import('@/views/pavement/index.vue')
const Patrol = () => import('@/views/patrol/index.vue')
const Disease = () => import('@/views/disease/index.vue')
const Repair = () => import('@/views/repair/index.vue')
const Material2 = () => import('@/views/material2/index.vue')
const Machine = () => import('@/views/machine/index.vue')
const Emergency = () => import('@/views/emergency/index.vue')
const Deicing = () => import('@/views/deicing/index.vue')
const Occupy = () => import('@/views/occupy/index.vue')
const Greening = () => import('@/views/greening/index.vue')
const Safety2 = () => import('@/views/safety2/index.vue')
const Geom = () => import('@/views/geom/index.vue')
const Light = () => import('@/views/light/index.vue')
const Drain = () => import('@/views/drain/index.vue')
const Plan = () => import('@/views/plan/index.vue')
const PlanDetail = () => import('@/views/plan/detail.vue')
const Complaint = () => import('@/views/complaint/index.vue')
const Load = () => import('@/views/load/index.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/facility', name: 'facility', component: Facility },
    { path: '/bridge', name: 'bridge', component: Bridge },
    { path: '/tunnel', name: 'tunnel', component: Tunnel },
    { path: '/pavement', name: 'pavement', component: Pavement },
    { path: '/patrol', name: 'patrol', component: Patrol },
    { path: '/disease', name: 'disease', component: Disease },
    { path: '/repair', name: 'repair', component: Repair },
    { path: '/material2', name: 'material2', component: Material2 },
    { path: '/machine', name: 'machine', component: Machine },
    { path: '/emergency', name: 'emergency', component: Emergency },
    { path: '/deicing', name: 'deicing', component: Deicing },
    { path: '/occupy', name: 'occupy', component: Occupy },
    { path: '/greening', name: 'greening', component: Greening },
    { path: '/safety2', name: 'safety2', component: Safety2 },
    { path: '/geom', name: 'geom', component: Geom },
    { path: '/light', name: 'light', component: Light },
    { path: '/drain', name: 'drain', component: Drain },
    { path: '/plan', name: 'plan', component: Plan },
    { path: '/plan/:id', name: 'plan-detail', component: PlanDetail },
    { path: '/complaint', name: 'complaint', component: Complaint },
    { path: '/load', name: 'load', component: Load },
  ],
})

export default router
