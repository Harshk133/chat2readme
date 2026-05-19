import Image from "next/image";
import Link from "next/link";

const Footer = () => {
  return (
    <footer className="w-full py-8 text-center text-zinc-500 text-sm mt-auto z-10 relative">
      <div className="max-w-7xl mx-auto px-6 flex flex-col items-center justify-center gap-4">
        <div className="flex gap-6">
          <Link href="https://github.com/Harshk133/chat2readme" target="_blank" className="hover:text-white transition">
            GitHub
          </Link>
          <Link href="https://twitter.com" target="_blank" className="hover:text-white transition">
            Twitter
          </Link>
          <Link href="https://discord.com" target="_blank" className="hover:text-white transition">
            Discord
          </Link>
        </div>
        <p>© {new Date().getFullYear()} Chat2Readme. All rights reserved.</p>
      <Image width={700} height={700} src={"/Chat2Readme.png"} alt="logo" />
      </div>
    </footer>
  );
};

export default Footer;
