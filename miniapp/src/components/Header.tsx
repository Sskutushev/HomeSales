import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="absolute top-[10px] left-1/2 -translate-x-1/2 w-[1240px] h-[50px] bg-gray-800 text-white p-4 flex items-center justify-end">
      <div className="w-[50px] h-[50px] flex items-center justify-center">
        <img src="/HomeSales/logo.png" alt="HomeSale Logo" className="h-full w-full object-contain" />
      </div>
    </header>
  );
};

export default Header;
