import { NavLink } from "react-router-dom";

type Props = {
  to: string;
  label: string;
  onClick?: () => void;
};

const NavItem = ({ to, label, onClick }: Props) => (
  <NavLink
    to={to}
    onClick={onClick}
    className="group inline-block px-1 py-0.5 text-lg font-medium relative transition"
  >
    {({ isActive }: { isActive: boolean }) => (
      <span className="relative inline-block">
        <span
          className={`relative z-10 transition
            ${
              isActive
                ? "text-transparent bg-clip-text bg-gradient-to-r dark:from-pink-500 dark:via-yellow-500 dark:to-green-500 from-indigo-700 via-violet-800 to-rose-600"
                : "text-gray-800 dark:text-gray-300 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r dark:group-hover:from-pink-500 dark:group-hover:via-yellow-500 dark:group-hover:to-green-500 group-hover:from-indigo-700 group-hover:via-violet-800 group-hover:to-rose-600"
            }`}
        >
          {label}
        </span>
        <span className="absolute left-0 -bottom-0.5 h-[2px] w-0 bg-gradient-to-r dark:from-pink-500 dark:via-yellow-500 dark:to-green-500 from-indigo-700 via-violet-800 to-rose-600 transition-all duration-300 group-hover:w-full z-0"></span>
      </span>
    )}
  </NavLink>
);
export default NavItem;
