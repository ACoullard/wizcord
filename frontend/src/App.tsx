import './App.css'
import React from 'react';
import MainScreen from "./features/main/MainScreen";
import LoginPage from "./features/user-management/LoginPage";
import { createBrowserRouter, Router, RouterProvider } from 'react-router-dom';
import LandingPage from './features/user-management/LandingPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
    errorElement: <div>404 Not Found</div>,
  },
  {
    // path: '/',
    path: '/login',
    element: <LoginPage />,
    errorElement: <div>404 Not Found</div>,
  },
  {
    path: '/wizcord',
    element: <MainScreen />,
  }
]);

function App() {
  return (
    <>
      <RouterProvider router={router}/>
    </>
  )
}

export default App
