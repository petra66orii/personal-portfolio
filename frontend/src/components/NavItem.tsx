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
    className="group inline-block px-1 py-0.5 text-lg font-medium relative transition-colors duration-200"
  >
    {({ isActive }: { isActive: boolean }) => (
      <span className="relative inline-block">
        <span
          className={`relative z-10 transition-colors duration-200 ${
            isActive ? "nav-text-active" : "nav-text"
          }`}
        >
          {label}
        </span>
        <span className="absolute left-0 -bottom-0.5 h-[2px] w-0 logo-gradient transition-all duration-300 group-hover:w-full z-0"></span>
      </span>
    )}
  </NavLink>
);
export default NavItem;
