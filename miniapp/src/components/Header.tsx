import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-gray-800 text-white p-4 flex items-center">
      <img src="/HomeSales/logo.png" alt="HomeSale Logo" className="h-12 w-12 mr-4" />
      <h1 className="text-2xl font-bold">HomeSales</h1>
    </header>
  );
};

export default Header;
